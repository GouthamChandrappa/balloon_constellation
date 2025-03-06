import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class BalloonDataFetcher:
    """
    Class to fetch and process balloon constellation data from WindBorne Systems API
    """
    
    def __init__(self):
        self.base_url = "https://a.windbornesystems.com/treasure/"
        self.hours_available = 24  # Data available for the last 24 hours
    
    def fetch_data(self, hours_ago=0):
        """
        Fetch data from a specific time point
        
        Args:
            hours_ago (int): Hours in the past to fetch (0 for current, 1-23 for historical)
            
        Returns:
            list: Processed balloon data
        """
        if not (0 <= hours_ago < self.hours_available):
            raise ValueError(f"hours_ago must be between 0 and {self.hours_available-1}")
        
        # Format URL with leading zeros
        url = f"{self.base_url}{hours_ago:02d}.json"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()
            
            # Process the data into a more usable format
            return self._process_data(data, hours_ago)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {url}")
            return []
    
    def _process_data(self, data, hours_ago):
        """
        Process raw data into usable format
        
        Args:
            data (list): Raw data from API
            hours_ago (int): Hours ago this data represents
            
        Returns:
            list: List of dictionaries with processed balloon data
        """
        timestamp = datetime.now() - timedelta(hours=hours_ago)
        processed_data = []
        
        # Skip empty first element if present
        if data and len(data) > 0 and not data[0]:
            data = data[1:]
        
        # Process each balloon's coordinates
        for i, coords in enumerate(data):
            if not coords or len(coords) != 3:
                continue  # Skip invalid data points
                
            try:
                lat, lon, altitude = coords
                
                # Basic validation
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    continue  # Skip invalid coordinates
                
                processed_data.append({
                    'balloon_id': i,
                    'latitude': lat,
                    'longitude': lon,
                    'altitude': altitude,  # Assuming altitude is in km
                    'timestamp': timestamp.isoformat(),
                    'hours_ago': hours_ago
                })
            except (ValueError, TypeError):
                continue  # Skip if data format is unexpected
        
        return processed_data
    
    def fetch_historical_data(self, hours=24):
        """
        Fetch data for multiple hours in the past
        
        Args:
            hours (int): Number of hours of historical data to fetch
            
        Returns:
            list: Combined historical data for all available hours
        """
        hours = min(hours, self.hours_available)
        all_data = []
        
        for h in range(hours):
            data = self.fetch_data(hours_ago=h)
            all_data.extend(data)
        
        return all_data
    
    def get_dataframe(self, hours=24):
        """
        Get all data as a pandas DataFrame
        
        Args:
            hours (int): Number of hours of historical data to fetch
            
        Returns:
            pandas.DataFrame: DataFrame with all balloon data
        """
        data = self.fetch_historical_data(hours)
        return pd.DataFrame(data)
    
    def get_trajectories(self):
        """
        Group data by balloon ID to get trajectories
        
        Returns:
            dict: Dictionary mapping balloon IDs to their position history
        """
        df = self.get_dataframe()
        trajectories = {}
        
        for balloon_id, group in df.groupby('balloon_id'):
            # Sort by timestamp (newer first)
            sorted_positions = group.sort_values('hours_ago')
            trajectories[balloon_id] = sorted_positions.to_dict('records')
        
        return trajectories

# Example usage
if __name__ == "__main__":
    fetcher = BalloonDataFetcher()
    
    # Get current balloon positions
    current_data = fetcher.fetch_data(hours_ago=0)
    print(f"Current balloon count: {len(current_data)}")
    
    # Get all historical data
    all_data = fetcher.fetch_historical_data()
    print(f"Total data points: {len(all_data)}")
    
    # Convert to DataFrame for analysis
    df = fetcher.get_dataframe()
    print(df.head())
    
    # Get trajectories by balloon ID
    trajectories = fetcher.get_trajectories()
    print(f"Number of unique balloons: {len(trajectories)}")