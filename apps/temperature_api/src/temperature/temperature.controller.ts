import { Controller, Get, Param, Query } from '@nestjs/common';
import { TemperatureService } from './temperature.service';

@Controller('temperature')
export class TemperatureController {
  constructor(private readonly temperatureService: TemperatureService) {}

  @Get()
  getTemperature(
    @Query('location') location?: string,
    @Query('sensor_id') sensorId?: string,
    @Query('sensorId') sensorIdCamel?: string,
  ) {
    const sId = sensorId || sensorIdCamel;
    if (location) {
      return this.temperatureService.getTemperatureByLocation(location);
    }
    if (sId) {
      return this.temperatureService.getTemperatureBySensorId(sId);
    }
    return this.temperatureService.getTemperatureBySensorId('0');
  }

  @Get(':sensorID')
  getTemperatureByParam(@Param('sensorID') sensorID: string) {
    return this.temperatureService.getTemperatureBySensorId(sensorID);
  }
}
