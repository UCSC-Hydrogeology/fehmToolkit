function assert_files_match(file1, file2)
    file1_contents = fileread(file1);
    file2_contents = fileread(file2);
    try
        assert(strcmp(file1_contents, file2_contents));
    catch e
        sprintf('Output (%s) does not match fixture (%s)', file1, file2)
        rethrow(e);
    end
end
