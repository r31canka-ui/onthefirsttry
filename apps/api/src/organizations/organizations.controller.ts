import { Body, Controller, Get, Patch } from '@nestjs/common';
import { OrganizationsService } from './organizations.service';
import { RequirePermissions } from '../common/decorators/require-permissions.decorator';
import { UpdateOrganizationDto } from './dto/update-organization.dto';

@Controller('organizations')
export class OrganizationsController {
  constructor(private readonly organizationsService: OrganizationsService) {}

  @Get('me')
  getMine() {
    return this.organizationsService.getMine();
  }

  @RequirePermissions('organization.manage')
  @Patch('me')
  update(@Body() dto: UpdateOrganizationDto) {
    return this.organizationsService.update(dto);
  }
}
