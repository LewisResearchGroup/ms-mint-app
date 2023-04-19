import pandas as pd
from pathlib import Path as P

from ms_mint_app import tools as T

def test__merge_metadata():
    # Define the old DataFrame
    old_data = {
      "MS-file": ["file1", "file2", "file3"],
      "col1": [1, 2, 3],
      "col2": ["a", "b", "c"],
      "col3": ["x", "y", "z"]
    }
    old_df = pd.DataFrame(data=old_data)

    # Define the new DataFrame
    new_data = {
      "MS-file": ["file1", "file2", "file3", "not-in-old"],
      "col1": [1, 2, 6, 7],
      "col2": ["d", "b", "f", "g"],
      "new_col": ['i', 'j', 'k', 'l']
    }
    new_df = pd.DataFrame(data=new_data)

    # Define the new DataFrame
    expected = {
      "MS-file": ["file1", "file2", "file3"],
      "col1": [1, 2, 6],
      "col2": ["d", "b", "f"],
      "col3": ["x", "y", "z"],
      "new_col": ['i', 'j', 'k']
    }
    expected_df = pd.DataFrame(data=expected)

    actual_df = T.merge_metadata(old_df, new_df)
    
    print('Old datafame:')
    print(old_df)
    print('New datafame:')
    print(new_df)
    print('Expected result:')
    print(expected_df)
    print('Actual result:')
    print(actual_df)

    assert actual_df.equals(expected_df), actual_df
    
    

def test__get_metadata(tmp_path):
    
    T.create_workspace(tmp_path, 'test')
    
    # Create working directory
    wdir = P(tmp_path/'workspaces', 'test')

    ms_files_path = P(wdir/'ms_files')
    
    # Create files
    open(ms_files_path/'F1.mzXML', 'w').close()
    open(ms_files_path/'F2.mzXML', 'w').close()
  
    for subpath in P(tmp_path).rglob('*'):
        print(subpath)
    
    metadata = T.get_metadata(wdir)
    
    print(metadata)
    
    for e in metadata['MS-file']:
        print(f'"{e}"')
    
    assert 'F1' in list(metadata['MS-file']), metadata
    assert 'F2' in list(metadata['MS-file']), metadata
        
    

def test__get_metadata_after_more_files_added(tmp_path):
    
    T.create_workspace(tmp_path, 'test')
    
    # Create working directory
    wdir = P(tmp_path/'workspaces', 'test')

    ms_files_path = P(wdir/'ms_files')
    
    # Create files
    open(ms_files_path/'F1.mzXML', 'w').close()
    open(ms_files_path/'F2.mzXML', 'w').close()
  
    for subpath in P(tmp_path).rglob('*'):
        print(subpath)
    
    metadata = T.get_metadata(wdir)
    
    print(metadata)
    
    T.write_metadata(metadata, wdir)
    
    # Create more files
    open(ms_files_path/'F3.mzXML', 'w').close()
    open(ms_files_path/'F4.mzXML', 'w').close()    
    
    for subpath in P(tmp_path).rglob('*'):
        print(subpath)
        
    metadata = T.get_metadata(wdir)

    print(metadata)

    assert all( metadata.PeakOpt == False)