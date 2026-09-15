import {
  ArgumentsHost,
  Catch,
  ExceptionFilter,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Prisma } from '@prisma/client';
import { Response } from 'express';

@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  private readonly logger = new Logger(AllExceptionsFilter.name);

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    if (exception instanceof HttpException) {
      const status = exception.getStatus();
      response.status(status).json(exception.getResponse());
      return;
    }

    // Postgres exclusion constraint violation (double-booking) surfaces as
    // Prisma P2004 "A constraint failed on the database" with the Postgres
    // constraint name in meta.database_error, since Prisma has no first-class
    // concept of EXCLUDE constraints.
    if (
      exception instanceof Prisma.PrismaClientKnownRequestError &&
      exception.code === 'P2004' &&
      typeof exception.meta?.database_error === 'string' &&
      exception.meta.database_error.includes('appointments_no_double_booking')
    ) {
      response.status(HttpStatus.CONFLICT).json({
        statusCode: HttpStatus.CONFLICT,
        message: 'This provider already has an appointment that overlaps this time range.',
      });
      return;
    }

    if (exception instanceof Prisma.PrismaClientKnownRequestError && exception.code === 'P2025') {
      response.status(HttpStatus.NOT_FOUND).json({
        statusCode: HttpStatus.NOT_FOUND,
        message: 'Not found.',
      });
      return;
    }

    this.logger.error(exception instanceof Error ? exception.stack : exception);
    response.status(HttpStatus.INTERNAL_SERVER_ERROR).json({
      statusCode: HttpStatus.INTERNAL_SERVER_ERROR,
      message: 'Internal server error.',
    });
  }
}
