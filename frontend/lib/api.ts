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
  return response.json();
};