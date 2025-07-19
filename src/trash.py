import subprocess as sp
import traceback
from cmd import Cmd

import pandas as pd

from typing import Any
from typing_extensions import Self

from glob import glob
from pprint import pprint, saferepr
from termcolor import colored

def sep(width:int=80, sep:str='-'):
    print(sep * width)

class Shell(Cmd):

    selected:   str|None = None
    track:      pd.DataFrame|None = None

    auto_opts:  list[str]

    intro  = 'TraSH: A Tracker Shell\n\nType \'help\' or ? to list commands\nType CTRL + D or \'quit\' to exit the shell\n'
    prompt = colored('trash', 'green')  + '$ '
    
    # region toplevel cmd

    def cmdloop(self, intro:str|None=None) -> None:
        while True:
            try:
                return Cmd.cmdloop(self, intro=self.intro)
            except KeyboardInterrupt:
                self.intro = None
                print("^C")
            except Exception as e:
                self.intro = None
                print(colored(f'Caught exception: {type(e)}', 'red'))
                print(colored(e, 'red'))
                if input('Show traceback? (y/N) ').lower() == 'y':
                    print(traceback.format_exc())
                continue

    def emptyline(self) -> bool:
        return Cmd.emptyline(self)
    
    def get_options(self, text:str, options:list[str]) -> list[str]:
        if not text:
            completions = options
        else:
            completions = [s for s in options if s.startswith(text)]
        return completions

    def autocomplete_last(self, text:str) -> list[str]:
        return self.get_options(text, self.auto_opts)

    def do_quit(self, args:str) -> None:
        '''
        Exit the shell
        '''
        print('Exiting...\n')
        exit(0)
    
    def do_EOF(self, args:str) -> None:
        '''
        Exit the shell on EOF (CTRL + D)
        '''

        print('^D\nExiting...\n')
        exit(1)

    def do_c(self, args:str) -> None:
        '''
        Clear the terminal
        '''
        sp.call(['clear'])

    # endregion

    def do_ld(self, args:str) -> None:
        '''
        ld [name]

        List all lists in the directory
        Loads a list with the provided name
        '''

        self.auto_opts = []
        SEARCH_PATH = 'lists/*.csv'
        
        argv:list|None = None
        if args:
            argv = args.split()

        if argv and len(argv) > 0:
            path = SEARCH_PATH.replace('*', argv[0])
            opts = glob(SEARCH_PATH)
            assert len(opts) == 1

            self.selected = argv[0]
            try:
                self.track = pd.read_csv(path, index_col=0)
                sel_prompt = colored(f'{self.selected}', 'blue') if self.selected is not None else ''
                self.prompt = colored('trash', 'green') + ':' + sel_prompt  + '$ '
            except FileNotFoundError:
                print(f'Cannot open {repr(path)}')
                
        else:
            opts = glob(SEARCH_PATH)
            print(SEARCH_PATH.split('/')[0])
            for o in opts:
                name = o.split('/')[1].rstrip('.csv')
                print(f'└──{name}')
                self.auto_opts.append(name)
    
    def complete_ld(self, text:str, line:str, begin:int, end:int) -> list[str]:
        return self.autocomplete_last(text)

    def do_l(self, args:str) -> None:
        '''
        l {name} [-ip]

        List all items in a list
        List all tems with given name(s) in a list

        -i  Ignore case sensitivity
        -p  Use name prefix
        '''
        
        if self.track is not None:
            
            argv:list|None = None
            if args:
                argv = args.split()

            if argv and len(argv) > 0:

                if set(argv) | set(['-p', '-i']):
                    raise NotImplementedError('list flags') # TODO 
                
                df = self.track.loc[list(set(argv) & set(self.track.index))]
                if df.empty:
                    print('No matching entries')
                else:
                    print(df)
            else:
                print(self.track)

    def complete_l(self, text:str, line:str, begin:int, end:int) -> list[str]:
        if self.track is not None:
            return self.get_options(text, self.track.index.tolist())
        return []

    def do_a(self, args:str) -> None:
        '''
        a [name]

        Add an entry to the list
        Add an entry with just the given name to the list
        '''
        raise NotImplementedError('add')

    def do_d(self, args:str) -> None:
        '''
        d <name> {name}

        Delete an entry with the given name(s) from the list
        '''
        raise NotImplementedError('delete')

    def do_f(self, args:str) -> None:
        '''
        f {filter=value}
        '''
        
        ...


def main() -> None:

    Shell().cmdloop()
    return

    df = pd.read_csv('lists/test.csv', index_col=0)
    print(df)
    sep()
    print(df.index)

    return


if __name__ == '__main__':
    main()