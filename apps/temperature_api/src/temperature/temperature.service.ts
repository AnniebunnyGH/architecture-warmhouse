import { Injectable } from '@nestjs/common';

@Injectable()
export class TemperatureService {
  getTemperatureByLocation(location: string) {
    let sensorId = '0';
    switch (location) {
      case 'Living Room':
        sensorId = '1';
        break;
      case 'Bedroom':
        sensorId = '2';
        break;
      case 'Kitchen':
        sensorId = '3';
        break;
      default:
        sensorId = '0';
    }
    return this.buildResponse(location, sensorId);
  }

  getTemperatureBySensorId(sensorId: string) {
    let location = 'Unknown';
    switch (sensorId) {
      case '1':
        location = 'Living Room';
        break;
      case '2':
        location = 'Bedroom';
        break;
      case '3':
        location = 'Kitchen';
        break;
      default:
        location = 'Unknown';
    }
    return this.buildResponse(location, sensorId);
  }

  private buildResponse(location: string, sensorId: string) {
    const value = parseFloat((15.0 + Math.random() * 13.0).toFixed(1));
    return {
      value,
      unit: 'CELSIUS',
      timestamp: new Date().toISOString(),
      location,
      status: 'active',
      sensor_id: sensorId,
      sensor_type: 'temperature',
      description: 'External temperature sensor data',
    };
  }
}
