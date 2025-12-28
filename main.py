#!/usr/bin/env python3

import asyncio
import os
from kasa import Discover, Credentials
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('KASA_USERNAME')
password = os.getenv('KASA_PASSWORD')
model = os.getenv('KASA_MODEL', "KP125M")

async def discover_devices():
    """Discover Kasa devices using cloud authentication."""
    
    if not username or not password:
        print("Please set KASA_USERNAME and KASA_PASSWORD in .env file for cloud-authenticated devices")
        return {}
    
    try:
        devices = await Discover.discover(
            credentials=Credentials(username, password)
        )
        return devices
    except Exception as e:
        print(f"Discovery with credentials failed: {e}")
        return {}

async def get_power_statistics(dev):
    """Get power statistics for a device."""
    if hasattr(dev, 'has_emeter'):
        try:
            await dev.update()
            power = dev.modules['Energy']
            return power
        except Exception as e:
            print(f"Error getting power statistics: {e}")
            return None
    return None

async def main():
    print("Exporter kasa-smartplug-exporter online!")
    
    devices = await discover_devices()
    
    if not devices:
        print("No devices found.")
        return
    print("Found devices via cloud authentication.")    
    print(f"Found {len(devices)} devices:")

    model_devices = []
    
    for ip, dev in devices.items():
        print(f"\nDevice at {ip}:")
        print(f"Type: {type(dev).__name__}")
        
        try:
            # Update device to get current state
            await dev.update()
            
            print(f"Alias: {dev.alias}")
            print(f"Model: {dev.model}")
            
            # Filter by model if specified
            if model and model != dev.model:
                print(f"Skipping {dev.model} and disconnecting, looking for {model}")
                await dev.disconnect()
                continue
            
            # Add to model devices list
            model_devices.append(dev)
                            
        except Exception as e:
            print(f"Error getting device info: {e}")
            print("Note: This device may require cloud authentication")
            await dev.disconnect()
    
    print(f"\nFound {len(model_devices)} devices matching model '{model}':")
    for dev in model_devices:
        power = await get_power_statistics(dev)
        if power is not None:
            print(f"  {dev.alias} ({dev.model}): {power.status}W")
        else:
            print(f"  {dev.alias} ({dev.model}): Unable to get power reading")
    

    if not model_devices:
        print("No devices found matching the specified model.")
        return

    for dev in model_devices:
        try:
            await dev.disconnect()
        except Exception as e:
            print(f"Error disconnecting device: {e}")

    print("All devices disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
