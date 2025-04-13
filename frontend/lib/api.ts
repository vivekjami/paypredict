import { Invoice } from '@/types';

export const fetchInvoices = async (): Promise<Invoice[]> => {
  const response = await fetch('http://localhost:8000/api/invoices/', {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch invoices');
  }
  const data = await response.json();
  return data.map((invoice: Invoice) => ({
    ...invoice,
    amount: Number(invoice.amount), // Normalize to number
  }));
};