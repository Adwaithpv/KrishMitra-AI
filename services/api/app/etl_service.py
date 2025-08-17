"""
Simple ETL service for ingesting agricultural data.
"""

import os
import json
from typing import List, Dict, Any
from datetime import datetime
import requests
from pathlib import Path


class ETLService:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
    
    def ingest_sample_data(self) -> List[Dict[str, Any]]:
        """Ingest sample agricultural data"""
        sample_data = [
            {
                "text": "Rice requires 120-150 days to mature. Transplant 25-30 day old seedlings at 20x15 cm spacing.",
                "meta": {
                    "source": "icar_rice_guide.pdf",
                    "date": "2024-01-15",
                    "geo": "Karnataka",
                    "crop": "rice",
                    "topic": "planting"
                }
            },
            {
                "text": "Apply 60:40:40 kg/ha NPK for wheat. Split application: 50% at sowing, 25% at tillering, 25% at flowering.",
                "meta": {
                    "source": "wheat_fertilizer_guide.pdf",
                    "date": "2024-02-01",
                    "geo": "Punjab",
                    "crop": "wheat",
                    "topic": "fertilizer"
                }
            },
            {
                "text": "Monitor for yellow rust in wheat during February-March. Apply fungicide if disease severity exceeds 10%.",
                "meta": {
                    "source": "wheat_disease_alert.pdf",
                    "date": "2024-02-15",
                    "geo": "Haryana",
                    "crop": "wheat",
                    "topic": "disease_management"
                }
            },
            {
                "text": "Sugarcane requires 12-18 months. Plant in February-March or September-October. Maintain soil moisture.",
                "meta": {
                    "source": "sugarcane_calendar.pdf",
                    "date": "2024-01-20",
                    "geo": "Maharashtra",
                    "crop": "sugarcane",
                    "topic": "planting"
                }
            },
            {
                "text": "Cotton bollworm control: Apply Bt cotton or spray recommended insecticides at 5-7 day intervals.",
                "meta": {
                    "source": "cotton_pest_guide.pdf",
                    "date": "2024-03-01",
                    "geo": "Gujarat",
                    "crop": "cotton",
                    "topic": "pest_management"
                }
            },
            {
                "text": "Maize responds well to irrigation at knee-high, tasseling, and grain-filling stages. Avoid waterlogging.",
                "meta": {
                    "source": "maize_irrigation.pdf",
                    "date": "2024-02-10",
                    "geo": "Bihar",
                    "crop": "maize",
                    "topic": "irrigation"
                }
            },
            {
                "text": "Groundnut requires 90-120 days. Plant in June-July for kharif. Maintain proper spacing of 30x10 cm.",
                "meta": {
                    "source": "groundnut_guide.pdf",
                    "date": "2024-01-25",
                    "geo": "Andhra Pradesh",
                    "crop": "groundnut",
                    "topic": "planting"
                }
            },
            {
                "text": "Apply 20:40:20 kg/ha NPK for pulses. Inoculate seeds with Rhizobium for better nitrogen fixation.",
                "meta": {
                    "source": "pulses_fertilizer.pdf",
                    "date": "2024-02-05",
                    "geo": "Madhya Pradesh",
                    "crop": "pulses",
                    "topic": "fertilizer"
                }
            }
        ]
        
        # Save to file
        output_file = self.data_dir / "sample_agricultural_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        print(f"Ingested {len(sample_data)} sample documents to {output_file}")
        return sample_data
    
    def ingest_weather_data(self) -> List[Dict[str, Any]]:
        """
        Weather data is now handled by the Weather Agent using real-time API data.
        This method returns empty list to maintain compatibility.
        """
        print("Weather data is now provided by Weather Agent using real-time WeatherAPI.com data")
        return []
    
    def ingest_market_data(self) -> List[Dict[str, Any]]:
        """Ingest sample market price data"""
        market_data = [
            {
                "text": "Wheat prices stable at Rs 2,100/quintal in Punjab mandis. Good demand from flour mills expected.",
                "meta": {
                    "source": "agmarknet_prices.pdf",
                    "date": "2024-03-14",
                    "geo": "Punjab",
                    "crop": "wheat",
                    "topic": "market_prices"
                }
            },
            {
                "text": "Cotton prices increased by 5% to Rs 6,500/quintal. Export demand driving prices higher.",
                "meta": {
                    "source": "cotton_market_report.pdf",
                    "date": "2024-03-13",
                    "geo": "Gujarat",
                    "crop": "cotton",
                    "topic": "market_prices"
                }
            }
        ]
        
        output_file = self.data_dir / "market_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(market_data, f, indent=2, ensure_ascii=False)
        
        print(f"Ingested {len(market_data)} market documents to {output_file}")
        return market_data
    
    def get_all_data(self) -> List[Dict[str, Any]]:
        """Get all ingested data"""
        all_data = []
        
        # Add sample agricultural data
        all_data.extend(self.ingest_sample_data())
        
        # Weather data is now handled by Weather Agent using real-time API
        # No static weather data is ingested anymore
        
        # Add market data
        all_data.extend(self.ingest_market_data())
        
        return all_data
