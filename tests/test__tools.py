import pandas as pd
from ms_mint_app.tools import merge_metadata


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

    actual_df = merge_metadata(old_df, new_df)
    
    print('Old datafame:')
    print(old_df)
    print('New datafame:')
    print(new_df)
    print('Expected result:')
    print(expected_df)
    print('Actual result:')
    print(actual_df)

    assert actual_df.equals(expected_df), actual_df