import { IsOptional, IsIn } from 'class-validator';

export class FindConversationsQueryDto {
  @IsOptional()
  @IsIn(['asc', 'desc', '1', '-1'])
  sortByDate?: 'asc' | 'desc' | '1' | '-1';
}