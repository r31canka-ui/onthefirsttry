import { IsDateString, IsIn, IsOptional, IsString, IsUUID } from 'class-validator';

export class CreateAppointmentDto {
  @IsUUID('4')
  contactId: string;

  @IsUUID('4')
  providerUserId: string;

  @IsUUID('4')
  serviceId: string;

  @IsUUID('4')
  locationId: string;

  @IsDateString()
  startsAt: string;

  @IsOptional()
  @IsString()
  schedulingNote?: string;
}

export class UpdateAppointmentDto {
  @IsOptional()
  @IsDateString()
  startsAt?: string;

  @IsOptional()
  @IsUUID('4')
  providerUserId?: string;

  @IsOptional()
  @IsUUID('4')
  locationId?: string;

  @IsOptional()
  @IsString()
  schedulingNote?: string;
}

export class CancelAppointmentDto {
  @IsOptional()
  @IsString()
  reason?: string;
}

export class ListAppointmentsQueryDto {
  @IsOptional()
  @IsDateString()
  from?: string;

  @IsOptional()
  @IsDateString()
  to?: string;

  @IsOptional()
  @IsUUID('4')
  providerId?: string;

  @IsOptional()
  @IsUUID('4')
  locationId?: string;

  @IsOptional()
  @IsIn(['scheduled', 'completed', 'cancelled', 'no_show'])
  status?: string;
}

export class AvailabilityQueryDto {
  @IsUUID('4')
  providerId: string;

  @IsUUID('4')
  serviceId: string;

  @IsUUID('4')
  locationId: string;

  @IsDateString()
  date: string;
}
