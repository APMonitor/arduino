function output = urlread_apm(str)

try
    if usejava('jvm'),
        import com.mathworks.mlwidgets.io.InterruptibleStreamCopier;
        % use Java if available
        url = java.net.URL(str);
        urlConnect = url.openConnection;
        timeout = 1000000000;
        method = 'GET';
        urlConnect.setRequestMethod(upper(method));
        urlConnect.setReadTimeout(timeout);
        urlConnect.setDoOutput(true);
        outputStream = urlConnect.getOutputStream;
        outputStream.close;
        
        try
            inputStream = urlConnect.getInputStream;
            isGood = true;
        catch ME
            inputStream = urlConnect.getErrorStream;
            isGood = false;
            
            if isempty(inputStream)
                msg = ME.message;
                I = strfind(msg,char([13 10 9]));
                if ~isempty(I)
                    msg = msg(1:I(1)-1);
                end
                fprintf(2,'Response stream is undefined\n below is a Java Error dump (truncated):\n');
                error(msg)
            end
        end
        
        byteArrayOutputStream = java.io.ByteArrayOutputStream;
        isc = InterruptibleStreamCopier.getInterruptibleStreamCopier;
        isc.copyStream(inputStream,byteArrayOutputStream);
        inputStream.close;
        byteArrayOutputStream.close;
        
        output = char(typecast(byteArrayOutputStream.toByteArray','uint8'));
        % output = typecast(byteArrayOutputStream.toByteArray','uint8');
        
    else
        % urlread is sometimes slower after R2012a
        % use only if Java is not available
        output = urlread(url);
    end
    
catch Err    
    output = urlread(url);
end

end
