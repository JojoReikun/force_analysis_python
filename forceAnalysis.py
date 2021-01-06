"""
for testing and debugging in pycharm:
---> Tools
---> Python Console
---> (with ipython installed):
IN[1]: import lizardanalysis
---> run commands:
IN[2]: lizardanalysis.command(*args, **kwargs)
"""

from forceAnalysis import cli


def main():
    cli.main()


if __name__ == '__main__':
    main()