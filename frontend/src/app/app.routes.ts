import { Routes } from '@angular/router';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { AgentComponent } from './pages/agent/agent.component';
import { ActionsComponent } from './pages/actions/actions.component';
import { AuthGuard } from './core/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
  { path: 'agent', component: AgentComponent, canActivate: [AuthGuard] },
  { path: 'actions', component: ActionsComponent, canActivate: [AuthGuard] },
  { path: '**', redirectTo: 'dashboard' }
];
