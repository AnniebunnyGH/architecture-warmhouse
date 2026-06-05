import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { TemperatureController } from './temperature/temperature.controller';
import { TemperatureService } from './temperature/temperature.service';

@Module({
  imports: [],
  controllers: [AppController, TemperatureController],
  providers: [TemperatureService],
})
export class AppModule {}
