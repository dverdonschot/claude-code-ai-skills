#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests>=2.31.0",
#     "pandas>=2.0.0",
#     "diskcache>=5.6.0",
#     "pyarrow>=14.0.0",
# ]
# ///
"""CBS OData API Client using direct REST API calls"""

import requests
from typing import Optional, Dict, List, Any
import pandas as pd
from datetime import datetime, timedelta
from diskcache import Cache
from pathlib import Path


class CBSClient:
    """Client for interacting with CBS Open Data OData API"""

    BASE_URL = "https://opendata.cbs.nl/ODataApi/odata"

    def __init__(self, cache_dir: str = "./data/cache", cache_expiry_hours: int = 24, data_dir: str = "./data"):
        """
        Initialize CBS OData client

        Args:
            cache_dir: Directory for caching API responses
            cache_expiry_hours: Hours before cache expires
            data_dir: Base directory for storing datasets
        """
        self.session = requests.Session()
        self.cache = Cache(cache_dir)
        self.cache_expiry = timedelta(hours=cache_expiry_hours)
        self.data_dir = Path(data_dir)

    def _make_request(self, url: str) -> Dict[str, Any]:
        """
        Make HTTP request to CBS API

        Args:
            url: Full URL to request

        Returns:
            JSON response as dictionary
        """
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get metadata about a dataset

        Args:
            dataset_id: CBS dataset identifier

        Returns:
            Dictionary with dataset metadata
        """
        cache_key = f"info_{dataset_id}"
        cached = self.cache.get(cache_key)

        if cached:
            return cached

        url = f"{self.BASE_URL}/{dataset_id}/TableInfos"
        data = self._make_request(url)

        info = {}
        if 'value' in data and len(data['value']) > 0:
            info = data['value'][0]  # First (and only) table info

        self.cache.set(cache_key, info, expire=self.cache_expiry.total_seconds())
        return info

    def get_data_properties(self, dataset_id: str) -> pd.DataFrame:
        """
        Get all data properties/columns for a dataset

        Args:
            dataset_id: CBS dataset identifier

        Returns:
            DataFrame with property metadata
        """
        cache_key = f"properties_{dataset_id}"
        cached = self.cache.get(cache_key)

        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/{dataset_id}/DataProperties"
        data = self._make_request(url)

        properties = data.get('value', [])
        df = pd.DataFrame(properties)

        self.cache.set(cache_key, df, expire=self.cache_expiry.total_seconds())
        return df

    def get_dimensions(self, dataset_id: str, dimension_name: str) -> pd.DataFrame:
        """
        Get dimension values (e.g., Energiedragers, Perioden)

        Args:
            dataset_id: CBS dataset identifier
            dimension_name: Name of dimension (e.g., 'Energiedragers', 'Perioden')

        Returns:
            DataFrame with dimension values
        """
        cache_key = f"dim_{dataset_id}_{dimension_name}"
        cached = self.cache.get(cache_key)

        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/{dataset_id}/{dimension_name}"
        data = self._make_request(url)

        dimensions = data.get('value', [])
        df = pd.DataFrame(dimensions)

        self.cache.set(cache_key, df, expire=self.cache_expiry.total_seconds())
        return df

    def count_observations(self, dataset_id: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count total observations in dataset

        Args:
            dataset_id: CBS dataset identifier
            filters: Optional dictionary of filter conditions

        Returns:
            Total count of observations
        """
        url = f"{self.BASE_URL}/{dataset_id}/TypedDataSet/$count"
        params = {}

        if filters:
            filter_parts = []
            for field, value in filters.items():
                filter_parts.append(f"{field} eq '{value}'")
            params['$filter'] = ' and '.join(filter_parts)

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return int(response.text.strip())

    def get_data(
        self,
        dataset_id: str,
        select: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get dataset observations with optional filtering

        Args:
            dataset_id: CBS dataset identifier
            select: List of columns to select
            filters: Dictionary of filter conditions
            top: Limit number of results
            skip: Skip first N results

        Returns:
            DataFrame with dataset observations
        """
        url = f"{self.BASE_URL}/{dataset_id}/TypedDataSet"
        params = {}

        # Build OData query parameters
        if select:
            params['$select'] = ','.join(select)

        if filters:
            filter_parts = []
            for field, value in filters.items():
                filter_parts.append(f"{field} eq '{value}'")
            params['$filter'] = ' and '.join(filter_parts)

        if top:
            params['$top'] = top

        if skip:
            params['$skip'] = skip

        # Make request with parameters
        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        observations = data.get('value', [])
        return pd.DataFrame(observations)

    def list_entity_sets(self, dataset_id: str) -> List[str]:
        """
        List all available entity sets for a dataset

        Args:
            dataset_id: CBS dataset identifier

        Returns:
            List of entity set names
        """
        url = f"{self.BASE_URL}/{dataset_id}"
        data = self._make_request(url)

        # Extract entity set names from the service document
        entity_sets = []
        if 'value' in data:
            entity_sets = [item['name'] for item in data['value'] if 'name' in item]

        return entity_sets

    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()

    def list_datasets(self) -> pd.DataFrame:
        """
        List all available CBS datasets from the catalog

        Returns:
            DataFrame with dataset information (Identifier, Title, Modified, etc.)
        """
        import xml.etree.ElementTree as ET

        cache_key = "datasets_catalog"
        cached = self.cache.get(cache_key)

        if cached is not None:
            return cached

        # The CBS catalog uses a different endpoint with XML format
        url = "https://opendata.cbs.nl/ODataCatalog/Tables?$format=json"

        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()

        datasets = data.get('value', [])
        df = pd.DataFrame(datasets)

        # Cache for longer (datasets don't change frequently)
        self.cache.set(cache_key, df, expire=timedelta(days=7).total_seconds())
        return df

    def save_dataset(
        self,
        dataset_id: str,
        df: pd.DataFrame,
        filename: str = "data.parquet",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save dataset to structured directory with metadata

        Args:
            dataset_id: CBS dataset identifier
            df: DataFrame to save
            filename: Name of the parquet file (default: data.parquet)
            metadata: Optional metadata dictionary to save alongside

        Returns:
            Path to saved file
        """
        # Create dataset-specific directory
        dataset_dir = self.data_dir / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)

        # Save main data as parquet
        data_path = dataset_dir / filename
        df.to_parquet(data_path, index=False, engine='pyarrow')

        # Save metadata if provided
        if metadata:
            import json
            metadata_path = dataset_dir / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)

        return data_path

    def load_dataset(
        self,
        dataset_id: str,
        filename: str = "data.parquet"
    ) -> Optional[pd.DataFrame]:
        """
        Load dataset from structured directory

        Args:
            dataset_id: CBS dataset identifier
            filename: Name of the parquet file (default: data.parquet)

        Returns:
            DataFrame if found, None otherwise
        """
        data_path = self.data_dir / dataset_id / filename
        if data_path.exists():
            return pd.read_parquet(data_path)
        return None

    def save_dimension(
        self,
        dataset_id: str,
        dimension_name: str,
        df: pd.DataFrame
    ) -> Path:
        """
        Save dimension data to structured directory

        Args:
            dataset_id: CBS dataset identifier
            dimension_name: Name of dimension
            df: DataFrame with dimension data

        Returns:
            Path to saved file
        """
        dataset_dir = self.data_dir / dataset_id / "dimensions"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{dimension_name.lower()}.parquet"
        path = dataset_dir / filename
        df.to_parquet(path, index=False, engine='pyarrow')

        return path

    def load_dimension(
        self,
        dataset_id: str,
        dimension_name: str
    ) -> Optional[pd.DataFrame]:
        """
        Load dimension data from structured directory

        Args:
            dataset_id: CBS dataset identifier
            dimension_name: Name of dimension

        Returns:
            DataFrame if found, None otherwise
        """
        filename = f"{dimension_name.lower()}.parquet"
        path = self.data_dir / dataset_id / "dimensions" / filename
        if path.exists():
            return pd.read_parquet(path)
        return None


if __name__ == "__main__":
    # Simple test
    client = CBSClient()
    info = client.get_dataset_info("83140NED")
    print(f"Dataset: {info.get('Title', 'N/A')}")
    print(f"Period: {info.get('Period', 'N/A')}")
