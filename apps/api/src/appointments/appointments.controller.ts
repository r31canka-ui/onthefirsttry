import { Body, Controller, Get, Param, Patch, Post, Query } from '@nestjs/common';
import { AppointmentsService } from './appointments.service';
import { RequirePermissions } from '../common/decorators/require-permissions.decorator';
import {
  AvailabilityQueryDto,
  CancelAppointmentDto,
  CreateAppointmentDto,
  ListAppointmentsQueryDto,
  UpdateAppointmentDto,
} from './dto/appointment.dto';

@Controller('appointments')
export class AppointmentsController {
  constructor(private readonly appointmentsService: AppointmentsService) {}

  @Get()
  list(@Query() query: ListAppointmentsQueryDto) {
    return this.appointmentsService.list(query);
  }

  @Get('availability')
  availability(@Query() query: AvailabilityQueryDto) {
    return this.appointmentsService.availability(query);
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.appointmentsService.findOne(id);
  }

  @RequirePermissions('appointments.write')
  @Post()
  create(@Body() dto: CreateAppointmentDto) {
    return this.appointmentsService.create(dto);
  }

  @RequirePermissions('appointments.write')
  @Patch(':id')
  update(@Param('id') id: string, @Body() dto: UpdateAppointmentDto) {
    return this.appointmentsService.update(id, dto);
  }

  @RequirePermissions('appointments.write')
  @Post(':id/cancel')
  cancel(@Param('id') id: string, @Body() dto: CancelAppointmentDto) {
    return this.appointmentsService.cancel(id, dto);
  }

  @RequirePermissions('appointments.write')
  @Post(':id/complete')
  complete(@Param('id') id: string) {
    return this.appointmentsService.complete(id);
  }

  @RequirePermissions('appointments.write')
  @Post(':id/no-show')
  noShow(@Param('id') id: string) {
    return this.appointmentsService.noShow(id);
  }
}
