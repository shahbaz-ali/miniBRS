

class IgnoreWarnings():

    @staticmethod
    def ignore():
        import sys
        if not sys.warnoptions:
            import os, warnings
            warnings.simplefilter("ignore")  # Change the filter in this process
            os.environ["PYTHONWARNINGS"] = "ignore"  # Also affect subprocesses