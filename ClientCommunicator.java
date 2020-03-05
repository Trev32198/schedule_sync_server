// Networking functionality
import java.io.*;
import java.net.*;

// ArrayList
import java.util.ArrayList;

public class ClientCommunicator
{
    // Declare necessary variables privately
    private final String SUCCESS = "SUCCESS" + (char)(0x04);
    private final String FAILURE = "FAILURE" + (char)(0x04);
    private final int PORT = 24602;
    private final String SERVER = "127.0.0.1";
    private String username = "";
    private String password = "";
    private String authType = "pw";
    private String sq = "";
    private String sqa = "";
    private String authToken = password;
    private Socket connectionSocket = null;
    private DataOutputStream dataOutStream = null;
    private DataInputStream dataInStream = null;
    private String latestResult = "";
    // Sends command to server and gets its response
    private String sendToServer(String command, String args[]) throws UnknownHostException, IOException
    {
        String toSend = command;
        for (String arg : args)
        {
            toSend += "\n" + arg;
        }
        // EOF marker
        toSend += (char)(0x04);
        connectionSocket = new Socket(SERVER, PORT);
        dataOutStream = new DataOutputStream(connectionSocket.getOutputStream());
        dataInStream = new DataInputStream(connectionSocket.getInputStream());
        dataOutStream.write(toSend.getBytes("UTF-8"));
        ArrayList<Byte> byteString = new ArrayList<Byte>();
        while (true)
        {
            int b = dataInStream.read();
            if (b != -1)
            {
                byteString.add((byte)(b));
            }
            else
            {
                break;
            }
        }
        byte outputBytes[] = new byte[byteString.size()];
        for (int i = 0; i < byteString.size(); i++)
        {
            outputBytes[i] = byteString.get(i);
        }
        String output = new String(outputBytes, "UTF-8");
        dataInStream.close();
        dataOutStream.close();
        connectionSocket.close();
        return output;
    }
    // Allow the rest of the app to get the results returned from the server, minus
    // the SUCCESS, FAILURE, and EOF markers
    public String getLatestResult()
    {
        return latestResult.replace(SUCCESS, "").replace(FAILURE, "");
    }
    // A method for each of the commands the server supports
    // All commands / methods require authentication except createAccount
    // All commands / methods store their results in this->latestResult
    // All commands / methods return a boolean indicating success or failure
    public boolean createAccount(String username, String password,
                              String sq, String sqa)
    {
        // Update the class's credential storage so that after the user
        // is made the account can be immediately used in authentication
        this.username = username;
        this.password = password;
        this.sq = sq;
        this.sqa = sqa;
        this.authType = "pw";
        this.authToken = password;
        try
        {
            latestResult = sendToServer("CREATE ACCOUNT", new String[] {username, password,
                                                  sq, sqa});
            System.out.println(latestResult);
            if (latestResult.contains(SUCCESS))
            {
                // If we make it here, the account was successfully created
                // Update the class's credential storage so that after the user
                // is made the account can be immediately used in authentication
                this.username = username;
                this.password = password;
                this.sq = sq;
                this.sqa = sqa;
                this.authType = "pw";
                this.authToken = password;
            }
            return latestResult.contains(SUCCESS);
        }
        catch (UnknownHostException e) {return false;}
        catch (IOException e) {return false;}
    }
    public boolean changePW(String newPassword)
    {
        try
        {
            latestResult = sendToServer("CHANGE PASSWORD", new String[] {username, password, authType, newPassword});
            if (latestResult.contains(SUCCESS))
            {
                // If we make it here, we changed the password successfully,
                // so we should update the locally stored password
                password = newPassword;
            }
            return latestResult.contains(SUCCESS);
        }
        catch (UnknownHostException e) {return false;}
        catch (IOException e) {return false;}
    }
    public boolean changeSQ(String newSQ, String newSQA)
    {
        try
        {
            latestResult = sendToServer("CHANGE SQ", new String[] {username, password, authType, newSQ, newSQA});
            if (latestResult.contains(SUCCESS))
            {
                // If we make it here, we changed the sq and sqa successfully
                // Change it client side too
                sq = newSQ;
                sqa = newSQA;
            }
            return latestResult.contains(SUCCESS);
        }
        catch (UnknownHostException e) {return false;}
        catch (IOException e) {return false;}
    }
    public boolean deleteAccount()
    {
        try
        {
            latestResult = sendToServer("DELETE ACCOUNT", new String[] {username, password, authType});
            // If we make it here, the account has been deleted
            // We could reset the credentials in this instance, but trying to log in with empty
            // credentials will work no better than credentials that are no longer valid
            return latestResult.contains(SUCCESS);
        }
        catch (UnknownHostException e) {return false;}
        catch (IOException e) {return false;}
    }
    public boolean searchUser(String query)
    {
        try
        {
            latestResult = sendToServer("SEARCH USER", new String[] {username, password, authType, query});
            return latestResult.contains(SUCCESS);
        }
        catch (UnknownHostException e) {return false;}
        catch (IOException e) {return false;}
    }
    // Allow the user to set credentials and authentication type manually, just in case
    // security question authentication is needed
    public void setCredentials(String username, String authToken,
                              String authType)
    {
        this.username = username;
        this.authToken = authToken;
        this.authType = authType;
    }
    // May construct a ClientCommunicator with or without credentials
    // Credentials can be provided immediately or just before a command requiring authentication
    public ClientCommunicator(String username, String authToken,
                              String authType)
    {
        setCredentials(username, authToken, authType);
    }
    public ClientCommunicator() {}
}
