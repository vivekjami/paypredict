"use client";
import { useAuth0 } from '@auth0/auth0-react';
import { Button } from '@/components/ui/button';

const AuthGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loginWithRedirect, isLoading, logout } = useAuth0();

  if (isLoading) {
    return <div className="text-center p-6 text-muted-foreground">Loading...</div>;
  }

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto p-6 text-center">
        <h1 className="text-2xl mb-4">Welcome to PayPredict</h1>
        <Button onClick={() => loginWithRedirect({
          authorizationParams: {
            redirect_uri: 'http://localhost:3000',
            audience: 'https://api.paypredict.com',
          }
        })}>
          Log In
        </Button>
      </div>
    );
  }

  return (
    <>
      <div className="flex justify-end p-4">
        <Button
          variant="outline"
          onClick={() =>
            logout({ logoutParams: { returnTo: 'http://localhost:3000' } })
          }
        >
          Log Out
        </Button>
      </div>
      {children}
    </>
  );
};

export default AuthGuard;