#!/usr/bin/env python3

import asyncio
import os
import logging
from kasa import Discover, Credentials
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge

# Create Prometheus metrics
power_gauge = Gauge('kasa_smartplug_milliwatts', 'Current power consumption in milliwatts', ['device_alias', 'device_model'])
current_gauge = Gauge('kasa_smartplug_milliamperes', 'Current current consumption in milliamperes', ['device_alias', 'device_model'])
voltage_gauge = Gauge('kasa_smartplug_millivolts', 'Current voltage in millivolts', ['device_alias', 'device_model'])
energy_counter = Gauge('kasa_smartplug_energy_wh', 'Total energy consumption in watt-hours', ['device_alias', 'device_model'])

load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

username = os.getenv('KASA_USERNAME')
password = os.getenv('KASA_PASSWORD')
model_env = os.getenv('KASA_MODELS')
models = [m.strip() for m in model_env.split(',') if m.strip()] if model_env else []
port = int(os.getenv('PORT', 4467))
scrape_interval = int(os.getenv('POLL_INTERVAL', 10))

devices = []

async def collect_prometheus_metrics(dev):
    stats = await get_power_statistics(dev)
    
    if stats:
        power_gauge.labels(device_alias=dev.alias, device_model=dev.model).set(stats["power_mw"])
        current_gauge.labels(device_alias=dev.alias, device_model=dev.model).set(stats["current_ma"])
        voltage_gauge.labels(device_alias=dev.alias, device_model=dev.model).set(stats["voltage_mv"])
        energy_counter.labels(device_alias=dev.alias, device_model=dev.model).set(stats["energy_wh"])

async def discover_devices():    
    if not username or not password:
        logger.warning("Please set KASA_USERNAME and KASA_PASSWORD in .env file for cloud-authenticated devices")
        return {}
    
    try:
        devices = await Discover.discover(
            credentials=Credentials(username, password)
        )
        return devices
    except Exception as e:
        logger.error(f"Discovery with credentials failed: {e}")
        return {}

async def get_power_statistics(dev):
    if hasattr(dev, 'has_emeter'):
        try:
            await dev.update()
            power = dev.modules['Energy'].status
            logger.debug(f"  {dev.alias} ({dev.model}): {power['power_mw']}mW, {power['current_ma']}mA, {power['voltage_mv']}mV, {power['energy_wh']}Wh")
            return power
        except Exception as e:
            logger.error(f"Error getting power statistics: {e}")
            return None
    return None

# Note: aiohttp may print "Unclosed client session" warnings during shutdown.
# This is a cosmetic issue - connections are properly closed by the OS on exit.
# The warnings are harmless and can be ignored.
async def cleanup_devices():
    """Disconnect all devices."""
    global devices
    logger.info("Shutting down exporter...")
    for dev in devices:
        try:
            await dev.disconnect()
        except:
            pass
    logger.info("Devices disconnected.")
    logger.info("Exporter shutdown complete.")

async def main():
    logger.info("Exporter kasa-smartplug-exporter online!")
    
    global devices
    devices = await discover_devices()
    
    if not devices:
        logger.warning("No devices found.")
        return
    logger.info("Found devices via cloud authentication.")    
    logger.info(f"Found {len(devices)} devices:")

    model_devices = []
    
    for ip, dev in devices.items():
        logger.info(f"\nDevice at {ip}:")
        logger.info(f"Type: {type(dev).__name__}")
        
        try:
            # Update device to get current state
            await dev.update()
            
            logger.info(f"Alias: {dev.alias}")
            logger.info(f"Model: {dev.model}")
            
            if models and dev.model not in models:
                logger.warning(f"Skipping {dev.model} and disconnecting, looking for one of: {', '.join([f'\'{m}\'' for m in models])}")
                await dev.disconnect()
                continue
            
            # Add to model devices list
            model_devices.append(dev)
                            
        except Exception as e:
            logger.error(f"Error getting device info: {e}")
            logger.warning("Note: This device may require cloud authentication")
            await dev.disconnect()
    
    if not model_devices:
        logger.warning(f"No devices found matching the specified models: {', '.join([f'\'{m}\'' for m in models])}.")
        return

    logger.info(f"\nFound {len(model_devices)} devices matching models: {', '.join([f'\'{m}\'' for m in models])}:")
    for dev in model_devices:
        logger.info(f"\nDevice at {dev.host}:")
        logger.info(f"Type: {type(dev).__name__}")
        logger.info(f"Alias: {dev.alias}")
        logger.info(f"Model: {dev.model}")

    logger.info(f"Starting Prometheus Exporter server on port {port}...")
    logger.info(f"Scraping every {scrape_interval} seconds")
    start_http_server(port)

    logger.info(f"Prometheus metrics available at http://localhost:{port}/metrics")
    logger.info("Press Ctrl+C to stop the exporter.")

    try:
        while True:
            for dev in model_devices:
                await collect_prometheus_metrics(dev)

            await asyncio.sleep(scrape_interval)
    except asyncio.CancelledError:
        logger.info("\nReceived cancellation signal, cleaning up...")
    except KeyboardInterrupt:
        logger.info("\nReceived keyboard interrupt, cleaning up...")
    finally:
        await cleanup_devices()

if __name__ == "__main__":
    asyncio.run(main())
