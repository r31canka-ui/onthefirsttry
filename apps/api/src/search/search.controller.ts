import { Controller, Get, Query } from '@nestjs/common';
import { SearchService } from './search.service';
import { RequirePermissions } from '../common/decorators/require-permissions.decorator';

@Controller('search')
export class SearchController {
  constructor(private readonly searchService: SearchService) {}

  @RequirePermissions('contacts.read')
  @Get()
  search(@Query('q') q: string) {
    return this.searchService.search(q);
  }
}
