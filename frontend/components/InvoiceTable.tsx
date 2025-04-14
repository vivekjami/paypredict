
"use client";
import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Invoice } from '@/types';

interface InvoiceTableProps {
  invoices: Invoice[];
}

const InvoiceTable: React.FC<InvoiceTableProps> = ({ invoices }) => {
  const [filter, setFilter] = useState<string>('');

  const filteredInvoices = invoices.filter(
    (invoice) =>
      invoice.customer.name.toLowerCase().includes(filter.toLowerCase()) ||
      invoice.status.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div className="flex gap-4">
        <Input
          placeholder="Filter by customer or status..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="max-w-sm"
        />
        <Button variant="outline" onClick={() => setFilter('')}>
          Clear
        </Button>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Customer</TableHead>
            <TableHead>Amount</TableHead>
            <TableHead>Due Date</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Late Probability</TableHead>
            <TableHead>Expected Payment</TableHead>
            <TableHead>Risk</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredInvoices.length > 0 ? (
            filteredInvoices.map((invoice) => (
              <TableRow key={invoice.id}>
                <TableCell>{invoice.customer.name}</TableCell>
                <TableCell>${typeof invoice.amount === 'number' ? invoice.amount.toFixed(2) : invoice.amount}</TableCell>
                <TableCell>
                  {new Date(invoice.due_date).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <span
                    className={`px-2 py-1 rounded ${
                      invoice.status === 'paid'
                        ? 'bg-green-100 text-green-800'
                        : invoice.status === 'pending'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {invoice.status}
                  </span>
                </TableCell>
                <TableCell>
                  {invoice.prediction
                    ? `${(invoice.prediction.payment_probability * 100).toFixed(1)}%`
                    : 'N/A'}
                </TableCell>
                <TableCell>
                  {invoice.prediction
                    ? new Date(invoice.prediction.expected_date).toLocaleDateString()
                    : 'N/A'}
                </TableCell>
                <TableCell>
                  {invoice.prediction ? (
                    <span
                      className={`px-2 py-1 rounded ${
                        invoice.prediction.risk_level === 'low'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {invoice.prediction.risk_level}
                    </span>
                  ) : (
                    'N/A'
                  )}
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={7} className="text-center">
                No invoices found
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
};

export default InvoiceTable;