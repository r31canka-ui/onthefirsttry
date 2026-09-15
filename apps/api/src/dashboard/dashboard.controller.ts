import { Controller, Get } from '@nestjs/common';
import { DashboardService } from './dashboard.service';
import { RequirePermissions } from '../common/decorators/require-permissions.decorator';

@Controller('dashboard')
export class DashboardController {
  constructor(private readonly dashboardService: DashboardService) {}

  @RequirePermissions('reports.read')
  @Get('summary')
  summary() {
    return this.dashboardService.summary();
  }
}
