import pandas as pd
import numpy as np
import os
import openai
from dotenv import load_dotenv
from balloon_data_fetcher import BalloonDataFetcher

# Load environment variables
load_dotenv()

class BalloonAnalyzer:
    """Simple balloon data analyzer using OpenAI API directly"""
    
    def __init__(self, api_key=None):
        """Initialize with OpenAI API key"""
        # Get API key from .env file if not provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No OpenAI API key found. Set it in your .env file as OPENAI_API_KEY")
        
        # Set the API key
        openai.api_key = self.api_key
        
        # Create data fetcher
        self.fetcher = BalloonDataFetcher()
    
    def analyze_question(self, question):
        """Analyze a user question about the balloon data"""
        # Get data
        data_df = self.fetcher.get_dataframe()
        data_summary = self._create_data_summary(data_df)
        
        # Create prompt
        prompt = f"""
        You are an expert analyst for WindBorne Systems, a company that deploys weather balloons to collect atmospheric data. 
        Here's a summary of the current balloon data:
        {data_summary}
        
        User question: {question}
        
        Provide a clear, concise analysis that answers the question.
        Focus on patterns or insights that would be valuable for balloon operations.
        """
        
        # Call OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert weather balloon analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message["content"]
        except Exception as e:
            return f"Error connecting to OpenAI API: {str(e)}"
    
    def identify_anomalies(self):
        """Create a simple anomaly analysis for balloon data"""
        data_df = self.fetcher.get_dataframe()
        data_summary = self._create_data_summary(data_df)
        
        prompt = """
        You are an anomaly detection specialist for weather balloon systems.
        
        Based on the balloon data summary below, identify any potential anomalies or unusual patterns 
        in the balloon constellation. Focus on altitude outliers, unusual geographic distributions,
        or any other aspects that might indicate operational issues.
        
        Data summary:
        """ + data_summary
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in anomaly detection for atmospheric systems."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message["content"]
        except Exception as e:
            return f"Error generating anomaly analysis: {str(e)}"
    
    def get_launch_recommendations(self):
        """Generate simple launch recommendations"""
        data_df = self.fetcher.get_dataframe()
        data_summary = self._create_data_summary(data_df)
        
        prompt = """
        You are a strategic advisor for a weather balloon constellation.
        
        Based on the balloon data summary below, provide 2-3 recommended locations (with approximate
        latitude/longitude) where new balloons should be launched to optimize global coverage.
        Explain the rationale for each recommendation.
        
        Data summary:
        """ + data_summary
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in weather balloon deployment strategy."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message["content"]
        except Exception as e:
            return f"Error generating launch recommendations: {str(e)}"
    
    def _create_data_summary(self, df):
        """Create a simple summary of the balloon data"""
        if df.empty:
            return "No data available."
        
        # Basic stats
        balloon_count = df['balloon_id'].nunique()
        
        # Altitude stats
        avg_altitude = df['altitude'].mean()
        max_altitude = df['altitude'].max()
        min_altitude = df['altitude'].min()
        
        # Geographic distribution
        north_count = df[df['latitude'] > 0].shape[0]
        south_count = df[df['latitude'] < 0].shape[0]
        east_count = df[df['longitude'] > 0].shape[0]
        west_count = df[df['longitude'] < 0].shape[0]
        
        # Count balloons by region
        arctic = df[df['latitude'] > 66.5].shape[0]  # Arctic Circle
        antarctic = df[df['latitude'] < -66.5].shape[0]  # Antarctic Circle
        tropical = df[(df['latitude'] > -23.5) & (df['latitude'] < 23.5)].shape[0]  # Tropics
        
        summary = f"""
        Balloon Constellation Summary:
        - Total balloons tracked: {balloon_count}
        - Altitude range: {min_altitude:.2f} km to {max_altitude:.2f} km (avg: {avg_altitude:.2f} km)
        
        Geographic Distribution:
        - Northern/Southern Hemisphere: {north_count}/{south_count} balloons
        - Eastern/Western Hemisphere: {east_count}/{west_count} balloons
        - Arctic/Antarctic regions: {arctic}/{antarctic} balloons
        - Tropical region: {tropical} balloons
        """
        
        return summary