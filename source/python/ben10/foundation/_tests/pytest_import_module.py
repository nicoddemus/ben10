from ben10.foundation.callback import Callback
from ben10.foundation.import_module import ImportToken
import pytest


#===================================================================================================
# Test
#===================================================================================================
class Test:

    def testImportToken(self):
        csv_token = 'ben10.foundation.callback.Callback.INFO_POS_FUNC_CLASS'
        loaded_token = ImportToken(csv_token)
        assert loaded_token == Callback.INFO_POS_FUNC_CLASS

        # Testing for a token that does not exist
        error_token = 'coilib50.app.clipboard_interface.IClipboardObject.ERROR_TOKEN'
        with pytest.raises(ImportError):
            ImportToken(error_token)
