export interface Customer {
  id: string;
  name: string;
  email: string;
  credit_score: number;
}

export interface Invoice {
  id: string;
  customer: Customer;
  amount: number | string; // Allow string for API response
  due_date: string;
  status: 'pending' | 'paid' | 'overdue';
  created_at: string;
}