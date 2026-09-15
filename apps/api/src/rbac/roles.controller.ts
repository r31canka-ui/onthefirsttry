import { Body, Controller, Delete, Get, HttpCode, HttpStatus, Param, Patch, Post } from '@nestjs/common';
import { RolesService } from './roles.service';
import { RequirePermissions } from '../common/decorators/require-permissions.decorator';
import { CreateRoleDto, UpdateRoleDto } from './dto/role.dto';

@Controller()
export class RolesController {
  constructor(private readonly rolesService: RolesService) {}

  @Get('permissions')
  listPermissions() {
    return this.rolesService.listPermissions();
  }

  @Get('roles')
  listRoles() {
    return this.rolesService.listRoles();
  }

  @RequirePermissions('roles.manage')
  @Post('roles')
  createRole(@Body() dto: CreateRoleDto) {
    return this.rolesService.createRole(dto);
  }

  @RequirePermissions('roles.manage')
  @Patch('roles/:id')
  updateRole(@Param('id') id: string, @Body() dto: UpdateRoleDto) {
    return this.rolesService.updateRole(id, dto);
  }

  @RequirePermissions('roles.manage')
  @HttpCode(HttpStatus.NO_CONTENT)
  @Delete('roles/:id')
  deleteRole(@Param('id') id: string) {
    return this.rolesService.deleteRole(id);
  }
}
