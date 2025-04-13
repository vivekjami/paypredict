"use client";

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import InvoiceTable from './InvoiceTable';
import { fetchInvoices } from '@/lib/api';
import { Invoice } from '@/types';

const Dashboard: React.FC = () => {
  const { data: invoices, isLoading, error } = useQuery<Invoice[], Error>({
    queryKey: ['invoices'],
    queryFn: fetchInvoices,
  });

  return (
    <div className="container mx-auto p-6">
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-2xl">PayPredict Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center text-muted-foreground">
              Loading invoices...
            </div>
          ) : error ? (
            <div className="text-center text-red-500">
              Error: {error.message}
            </div>
          ) : (
            <InvoiceTable invoices={invoices || []} />
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;