from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import pandas as pd
import numpy as np
from balloon_data_fetcher import BalloonDataFetcher
import json

class BalloonAnalyzer:
    """
    Class to analyze balloon data using LLMs and LangChain
    """
    
    def __init__(self, api_key):
        """
        Initialize the analyzer with OpenAI API key
        
        Args:
            api_key (str): OpenAI API key
        """
        self.api_key = api_key
        self.fetcher = BalloonDataFetcher()
        self.llm = OpenAI(temperature=0, openai_api_key=api_key)
    
    def analyze_question(self, question):
        """
        Analyze a user question about the balloon data
        
        Args:
            question (str): User question
            
        Returns:
            str: Analysis result
        """
        # Get current data
        data_df = self.fetcher.get_dataframe()
        
        # Create a summary of the data for context
        data_summary = self._create_data_summary(data_df)
        
        # Create a prompt template
        template = """
        You are an expert analyst for WindBorne Systems, a company that deploys weather balloons to collect atmospheric data. 
        You have access to the current data about their balloon constellation.
        
        Here's a summary of the current balloon data:
        {data_summary}
        
        User question: {question}
        
        Provide a clear, concise, and insightful analysis that answers the question.
        Focus on patterns, anomalies, or operational insights that would be valuable for the WindBorne team.
        Make sure your analysis is specific to the balloon data provided.
        """
        
        prompt = PromptTemplate(
            input_variables=["data_summary", "question"],
            template=template,
        )
        
        # Create a chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Run the chain
        result = chain.run(data_summary=data_summary, question=question)
        
        return result.strip()
    
    def _create_data_summary(self, df):
        """
        Create a summary of the balloon data
        
        Args:
            df (pandas.DataFrame): DataFrame with balloon data
            
        Returns:
            str: Data summary
        """
        if df.empty:
            return "No data available."
        
        # Basic stats
        balloon_count = df['balloon_id'].nunique()
        current_balloons = df[df['hours_ago'] == 0].shape[0]
        
        # Altitude stats
        avg_altitude = df['altitude'].mean()
        max_altitude = df['altitude'].max()
        min_altitude = df['altitude'].min()
        
        # Geographic distribution
        north_count = df[df['latitude'] > 0].shape[0]
        south_count = df[df['latitude'] < 0].shape[0]
        east_count = df[df['longitude'] > 0].shape[0]
        west_count = df[df['longitude'] < 0].shape[0]
        
        # Movement analysis (if we have enough historical data)
        movement_analysis = ""
        if df['hours_ago'].nunique() > 1:
            # Group by balloon_id and sort by hours_ago
            trajectories = {}
            for balloon_id, group in df.groupby('balloon_id'):
                if group.shape[0] > 1:
                    # Sort by hours_ago (ascending)
                    sorted_group = group.sort_values('hours_ago', ascending=True)
                    
                    # Calculate distance traveled
                    if sorted_group.shape[0] >= 2:
                        first_pos = sorted_group.iloc[0]
                        last_pos = sorted_group.iloc[-1]
                        
                        # Simple distance calculation (not accounting for Earth's curvature)
                        dist_lat = last_pos['latitude'] - first_pos['latitude']
                        dist_lon = last_pos['longitude'] - first_pos['longitude']
                        
                        trajectories[balloon_id] = {
                            'distance_lat': dist_lat,
                            'distance_lon': dist_lon,
                            'hours': sorted_group['hours_ago'].max() - sorted_group['hours_ago'].min()
                        }
            
            if trajectories:
                # Calculate average movement
                avg_lat_movement = np.mean([t['distance_lat'] for t in trajectories.values()])
                avg_lon_movement = np.mean([t['distance_lon'] for t in trajectories.values()])
                
                movement_analysis = f"""
                Movement Analysis:
                - Average latitude change: {avg_lat_movement:.2f} degrees
                - Average longitude change: {avg_lon_movement:.2f} degrees
                - This indicates a general movement trend toward the {"north" if avg_lat_movement > 0 else "south"} and {"east" if avg_lon_movement > 0 else "west"}.
                """
        
        # Create the summary
        summary = f"""
        Balloon Constellation Summary:
        - Total unique balloons tracked: {balloon_count}
        - Current active balloons: {current_balloons}
        - Altitude range: {min_altitude:.2f} km to {max_altitude:.2f} km (avg: {avg_altitude:.2f} km)
        
        Geographic Distribution:
        - Northern Hemisphere: {north_count} observations
        - Southern Hemisphere: {south_count} observations
        - Eastern Hemisphere: {east_count} observations
        - Western Hemisphere: {west_count} observations
        
        {movement_analysis}
        
        The data includes the following for each balloon:
        - Balloon ID
        - Latitude and Longitude
        - Altitude in kilometers
        - Timestamp
        - Hours ago (0 for current, higher values for historical data)
        """
        
        return summary
    
    def get_launch_recommendations(self):
        """
        Generate launch recommendations based on current constellation data
        
        Returns:
            str: Launch recommendations
        """
        data_df = self.fetcher.get_dataframe()
        data_summary = self._create_data_summary(data_df)
        
        template = """
        You are an expert mission planner for WindBorne Systems, a company that deploys weather balloons to collect atmospheric data.
        Based on the current constellation data, provide recommendations for the next balloon launch.
        
        Current constellation data:
        {data_summary}
        
        Please provide:
        1. Recommended launch locations (up to 3) that would optimize global coverage
        2. Explanation of why these locations would be beneficial
        3. Any other strategic advice for the WindBorne team
        
        Make your recommendations specific and actionable.
        """
        
        prompt = PromptTemplate(
            input_variables=["data_summary"],
            template=template,
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(data_summary=data_summary)
        
        return result.strip()
    
    def identify_anomalies(self):
        """
        Identify anomalies in the balloon data
        
        Returns:
            str: Anomaly analysis
        """
        data_df = self.fetcher.get_dataframe()
        
        if data_df.empty:
            return "No data available for anomaly detection."
        
        # Perform basic anomaly detection
        # 1. Identify balloons with unusual altitudes
        altitude_mean = data_df['altitude'].mean()
        altitude_std = data_df['altitude'].std()
        altitude_outliers = data_df[
            (data_df['altitude'] > altitude_mean + 2*altitude_std) | 
            (data_df['altitude'] < altitude_mean - 2*altitude_std)
        ]
        
        # 2. Identify balloons with unusual movements
        movement_anomalies = []
        
        for balloon_id, group in data_df.groupby('balloon_id'):
            if group.shape[0] > 1:
                sorted_group = group.sort_values('hours_ago', ascending=True)
                
                # Check for sudden altitude changes
                if sorted_group.shape[0] >= 2:
                    for i in range(1, len(sorted_group)):
                        prev = sorted_group.iloc[i-1]
                        curr = sorted_group.iloc[i]
                        
                        # Calculate changes
                        alt_change = abs(curr['altitude'] - prev['altitude'])
                        lat_change = abs(curr['latitude'] - prev['latitude'])
                        lon_change = abs(curr['longitude'] - prev['longitude'])
                        
                        # Check for anomalies
                        if alt_change > 5 or lat_change > 15 or lon_change > 15:
                            movement_anomalies.append({
                                'balloon_id': balloon_id,
                                'from_hour': prev['hours_ago'],
                                'to_hour': curr['hours_ago'],
                                'alt_change': alt_change,
                                'lat_change': lat_change,
                                'lon_change': lon_change
                            })
        
        # Create summary of anomalies for the LLM
        anomaly_summary = f"""
        Altitude Anomalies:
        {altitude_outliers.shape[0]} balloons with unusual altitudes detected.
        
        Movement Anomalies:
        {len(movement_anomalies)} instances of unusual movement patterns detected.
        """
        
        template = """
        You are an expert analyst for WindBorne Systems specializing in anomaly detection.
        Based on the data analysis, provide insights about potential anomalies in the balloon constellation.
        
        Anomaly Detection Results:
        {anomaly_summary}
        
        Please provide:
        1. An assessment of these anomalies - are they concerning or expected?
        2. Possible explanations for the observed anomalies
        3. Recommendations for further investigation or action
        
        Keep your analysis concise and focused on operational implications.
        """
        
        prompt = PromptTemplate(
            input_variables=["anomaly_summary"],
            template=template,
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(anomaly_summary=anomaly_summary)
        
        return result.strip()

# Example usage
if __name__ == "__main__":
    analyzer = BalloonAnalyzer(api_key="your_openai_api_key")
    
    # Example question analysis
    question = "What are the current distribution patterns of balloons and what might this tell us about wind currents?"
    analysis = analyzer.analyze_question(question)
    print("Question Analysis:")
    print(analysis)
    print("\n" + "-"*50 + "\n")
    
    # Launch recommendations
    recommendations = analyzer.get_launch_recommendations()
    print("Launch Recommendations:")
    print(recommendations)
    print("\n" + "-"*50 + "\n")
    
    # Anomaly detection
    anomalies = analyzer.identify_anomalies()
    print("Anomaly Analysis:")
    print(anomalies)