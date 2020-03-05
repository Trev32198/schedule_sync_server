public class Tests
{
    // For testing only
    public static void main (String args[])
    {
        // Create an instance
        ClientCommunicator test = new ClientCommunicator();
        // Try creating a user
        boolean r1 = test.createAccount("Rusty123", "password123", "Who are you?", "Rusty");
        // Try changing the password
        boolean r2 = test.changePW("password123456");
        // Try changing the SQ
        boolean r3 = test.changeSQ("Who are you???", "Rustyyy");
        // Try searching for a user with 'e' in the name
        boolean r4 = test.searchUser("e");
        // See results
        System.out.println(test.getLatestResult());
        // Try deleting the account
        boolean r5 = test.deleteAccount();
        // See test results
        for (boolean i : new boolean[] {r1, r2, r3, r4, r5})
        {
            System.out.println(i);
        }
    }
}
