import { Routes } from '@angular/router'

export const routes: Routes = [
  { path: '', redirectTo: 'issues', pathMatch: 'full' },

  {
    path: 'issues',
    title: 'Issues · PayMatch',
    loadComponent: () =>
      import('./issues/issues-page').then((module) => module.IssuesPage)
  },

  {
    path: 'orders',
    title: 'Orders · PayMatch',
    loadComponent: () =>
      import('./orders/orders-page').then((module) => module.OrdersPage)
  },

  {
    path: 'payments',
    title: 'Payments · PayMatch',
    loadComponent: () =>
      import('./payments/payments-page').then((module) => module.PaymentsPage)
  },

  {
    path: 'sync-runs',
    title: 'Sync runs · PayMatch',
    loadComponent: () =>
      import('./sync-runs/sync-runs-page').then((module) => module.SyncRunsPage)
  },

  { path: '**', redirectTo: 'issues' }
]
