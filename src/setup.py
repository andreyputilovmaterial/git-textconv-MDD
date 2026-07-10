import argparse # for its main purpose
import traceback, sys # for error reporting and printing to stderr
from datetime import datetime, timezone # to capture timestamp, to be possibly used in debug print statements
from pathlib import Path # for its main purpose
import subprocess # to start subprocess, thanks captain obvious
import os # to get base python executable from within venv
import re # to assess existing git config


# STDOUT_COLOR_RED = "\033[91m"
STDOUT_COLOR_RED = "\033[31m"
STDOUT_COLOR_RESET = "\033[0m"
STDOUT_COLOR_GREEN = "\033[32m"



if __name__ == '__main__':
    # run as a program
    from GENERATED._VERSION import _VERSION as gittextconvmdd_script_version
    # NOTICE: if GENERATED is not found, re-run scripts/build.bat, or scripts/get_ver_file.bat
    from setup_files_data import files_data
elif '.' in __name__:
    # package
    from .GENERATED._VERSION import _VERSION as gittextconvmdd_script_version
    # NOTICE: if GENERATED is not found, re-run scripts/build.bat, or scripts/get_ver_file.bat
    from .setup_files_data import files_data
else:
    # included with no parent package
    from GENERATED._VERSION import _VERSION as gittextconvmdd_script_version
    # NOTICE: if GENERATED is not found, re-run scripts/build.bat, or scripts/get_ver_file.bat
    from setup_files_data import files_data



def write_program_files(path,files_data):
    """Self-written wrapper to write actual files to physical location"""
    output_root = Path(path).resolve()
    # print(f'Creating program files in {output_root}...')
    n_processed = 0

    for rel_path, content in files_data:
        file_path = output_root / rel_path

        # Create parent folders automatically
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(content, encoding="utf-8")
        n_processed += 1

    # print(f'{n_processed} files written')


def call_executable(subprocess_args,path,timeout,scope,input=None,allow_nonzero_status=False):
    """Self-written wrapper to ease launching of an executable
    
    Will grab outputs and manage it
    
    "scope" means part added to the beginning of every line in outputs"""
    # print(f'{scope}: launch executable; to verify: path == "{path}", callable == "{subprocess_args[0]}"')
    argsadd = {}
    if input:
        argsadd['input'] = input
    subprocess_results = subprocess.run(
        subprocess_args,
        cwd = path,
        capture_output=True,
        text=True,
        timeout=timeout,
        **argsadd,
        encoding='utf-8',
    )
    if subprocess_results.stdout.strip():
        for line in subprocess_results.stdout.splitlines(keepends=False):
            print(f'{scope}: {line}')
    if subprocess_results.stderr.strip():
        for line in subprocess_results.stderr.splitlines(keepends=False):
            print(f'{scope}: {STDOUT_COLOR_RED}{line}{STDOUT_COLOR_RESET}',file=sys.stderr)
    if not allow_nonzero_status:
        assert subprocess_results.returncode == 0, f'Failed:\nreturncode == {repr(subprocess_results.returncode)}'
    # print(f'success, status == {subprocess_results.returncode}')
    return subprocess_results


def get_python_base_exe():
    """Helper, I was thinking it helps address some issues with venv, but maybe this is unnecessary
    
    The goal is to point to real python executable for setting new venv
    
    Some fallback fn to find "system" python executable to set venv - but it looks it is not needed. The issue was very different"""
    try:
        env = os.environ.copy()
        env.pop('VIRTUAL_ENV',None)
        try:
            return sys.base_executable
        except AttributeError:
            try:
                return sys._base_executable
            except AttributeError:
                # try:
                #     return sys.executable
                # except:
                #     raise
                raise
    except Exception as e:
        print(f'Error: get_base_python_exe() failed, will fallback to default "python": {STDOUT_COLOR_RED}{e}{STDOUT_COLOR_RESET}',file=sys.stderr)
        return 'python'



def call_install_copy_program_files_program(*argcs,**kwargs):
    """Actually, installs files"""

    time_start = datetime.now()
    script_name = 'git-textconv-mdd script'

    parser = argparse.ArgumentParser(
        description="git-textconv-mdd",
        prog='git-textconv-mdd'
    )
    parser.add_argument(
        '--path',
        type=str,
        # help='Choose from: ...',
        required=True
    )
    # args = None
    # args_rest = None
    # if( ('arglist_strict' in runscript_config) and (not runscript_config['arglist_strict']) ):
    #     args, args_rest = parser.parse_known_args()
    # else:
    args = parser.parse_args(*argcs,**kwargs)
    
    path = None
    if args.path:
        path = Path(args.path)
        path = f'{path.resolve()}'
    else:
        raise FileNotFoundError('path: path not provided; please use --path option')
    
    path_python_executable = Path(path) / '.venv/Scripts/python.exe'

    print(f'{script_name}: script started at {time_start}')

    print(f'{script_name}: writing files to "{path}"')
    write_program_files(path,files_data)

    print(f'{script_name}: creating virtual environment...')
    subprocess_args = [
            get_python_base_exe(),
            '-m',
            'venv',
            '.venv',
        ]
    call_executable(subprocess_args,path,60,'venv')

    # print(f'{script_name}: debug: test sys.executable...')
    # subprocess_args = [
    #         path_python_executable,
    #         '-c',
    #         'import sys; print(sys.executable); print(sys.prefix)',
    #     ]
    # call_executable(subprocess_args,path,60,'venv: text sys.executable')

    # print(f'{script_name}: debug: test pip location...')
    # subprocess_args = [
    #         path_python_executable,
    #         '-m',
    #         'pip',
    #         '--version',
    #     ]
    # call_executable(subprocess_args,path,60,'venv: test pip path')

    print(f'{script_name}: installing dependencies...')
    subprocess_args = [
            path_python_executable,
            '-m',
            'pip',
            'install',
            '-r',
            'requirements.txt',
        ]
    call_executable(subprocess_args,path,60,'requirements.txt')

    print(f'{script_name}: {STDOUT_COLOR_GREEN}Done!"{STDOUT_COLOR_RESET}')

    time_finish = datetime.now()
    # print(f'{script_name}: finished at {time_finish} (elapsed {time_finish-time_start})')

def call_install_git_register_program(*argcs,**kwargs):
    """Adds global config to git"""

    def update_git_config(path):
        path_python_executable = Path(Path(path) / '.venv/Scripts/python.exe').resolve()
        path_py_script = Path(Path(path) / 'extract.py').resolve()
        subprocess_args = [
                'git',
                'config',
                '--global',
                'diff.mdd.textconv',
                f'"{path_python_executable}" "{path_py_script}"',
            ]
        call_executable(subprocess_args,path,60,'git config',allow_nonzero_status=True)
    
    def read_git_config():
        subprocess_args = [
                'git',
                'config',
                '--global',
                '--get',
                'diff.mdd.textconv',
            ]
        results = call_executable(subprocess_args,path,60,'git config',allow_nonzero_status=True)
        return results.stdout
    
    def safety_validate_existing_git_config(config_str):
        # results = read_git_config()
        results = config_str
        if not results:
            return True
        if re.match(r'.*\bextract.py\b(?:\s+[\-\w]+)*[\\"\']*',results):
            return True
        return False

    time_start = datetime.now()
    script_name = 'git-textconv-mdd script'

    parser = argparse.ArgumentParser(
        description="git-textconv-mdd",
        prog='git-textconv-mdd'
    )
    parser.add_argument(
        '--path',
        type=str,
        # help='Choose from: ...',
        required=True
    )
    # args = None
    # args_rest = None
    # if( ('arglist_strict' in runscript_config) and (not runscript_config['arglist_strict']) ):
    #     args, args_rest = parser.parse_known_args()
    # else:
    args = parser.parse_args(*argcs,**kwargs)
    
    path = None
    if args.path:
        path = Path(args.path)
        path = f'{path.resolve()}'
    else:
        raise FileNotFoundError('path: path not provided; please use --path option')
    
    # print(f'{script_name}: script started at {time_start}')

    existing_config = read_git_config()
    safety_validate = safety_validate_existing_git_config(existing_config)
    if safety_validate:
        print(f'Checking existing config: passed ({existing_config})')
    else:
        print(f'Checking existing config: {STDOUT_COLOR_RED}failed{STDOUT_COLOR_RESET} ({existing_config})')
        sys.exit(0)
    
    update_git_config(path)

    print(f'{script_name}: {STDOUT_COLOR_GREEN}Done!"{STDOUT_COLOR_RESET}')

    time_finish = datetime.now()
    # print(f'{script_name}: finished at {time_finish} (elapsed {time_finish-time_start})')

def call_install_git_update_global_gitattributes(*argcs,**kwargs):
    """Adds global config to git"""

    def update_git_config(path):
        path_gitattributes_global = path
        subprocess_args = [
                'git',
                'config',
                '--global',
                'core.attributesFile',
                f'{path_gitattributes_global}',
            ]
        call_executable(subprocess_args,'.',60,'git config',allow_nonzero_status=True)
    
    def read_git_config():
        subprocess_args = [
                'git',
                'config',
                '--global',
                '--get',
                'core.attributesFile',
            ]
        results = call_executable(subprocess_args,'.',60,'git config',allow_nonzero_status=True)
        return results.stdout
    
    time_start = datetime.now()
    script_name = 'git-textconv-mdd script'

    parser = argparse.ArgumentParser(
        description="git-textconv-mdd",
        prog='git-textconv-mdd'
    )
    parser.add_argument(
        '--path',
        type=str,
        # help='Choose from: ...',
        required=True
    )
    # args = None
    # args_rest = None
    # if( ('arglist_strict' in runscript_config) and (not runscript_config['arglist_strict']) ):
    #     args, args_rest = parser.parse_known_args()
    # else:
    args = parser.parse_args(*argcs,**kwargs)
    
    path = None
    if args.path:
        path = Path(args.path)
        path = f'{path.resolve()}'
    else:
        raise FileNotFoundError('path: path not provided; please use --path option')
    
    # print(f'{script_name}: script started at {time_start}')

    existing_config = read_git_config()
    if not existing_config:
        # let's create one
        print(f'global .gitattributes is not configured; we\'ll create one: {path}')
        write_program_files(Path(Path(path).parent).resolve(),[(Path(path).name,'*.mdd diff=mdd\n*.mrs linguist-language=VBScript\n*.dms linguist-language=VBScript\n')])
        assert Path(path).is_file()
        update_git_config(path)
        print(f'{script_name}: {STDOUT_COLOR_GREEN}Done!"{STDOUT_COLOR_RESET}')
    else:
        path = existing_config.strip()
        if Path(path).is_file():
            print('global .gitattributes is configured and does exist')
            gitattributes_content = None
            with open(path,'r',encoding='utf-8') as f:
                gitattributes_content = f.read()
            if re.match(r'^\s*?\*\.mdd\b[^\n]*?diff=',gitattributes_content,flags=re.M):
                print('pattern found, skip')
                sys.exit(0)
            else:
                print('pattern not found, adding...')
                with open(path,'a',encoding='utf-8') as f:
                    f.write('*.mdd diff=mdd\n')
            print(f'{script_name}: {STDOUT_COLOR_GREEN}Done!"{STDOUT_COLOR_RESET}')
        else:
            print('global .gitattributes is configured but does not exist; exit')
            sys.exit(0)

    time_finish = datetime.now()
    # print(f'{script_name}: finished at {time_finish} (elapsed {time_finish-time_start})')


def call_install_program(*argcs,**kwargs):
    """Wrapper for calling individual install scripts - depending on value of --action param"""

    time_start = datetime.now()
    script_name = 'git-textconv-mdd script'

    run_install_actions = {
        'copy-program-files': call_install_copy_program_files_program,
        'git-register': call_install_git_register_program,
        'git-set-global-gitattributes': call_install_git_update_global_gitattributes,
    }

    parser = argparse.ArgumentParser(
        description="git-textconv-mdd",
        prog='git-textconv-mdd'
    )
    parser.add_argument(
        '--action',
        type=str,
        # help='Choose from: ...',
        choices=dict.keys(run_install_actions),
        required=True
    )
    args, args_rest = parser.parse_known_args(*argcs,**kwargs)
    if args.action:
        program = '{arg}'.format(arg=args.action)
        if program in run_install_actions:
            run_install_actions[program](args_rest)
        else:
            raise AttributeError('action to be taken not recognized: {program}'.format(program=args.action))
    else:
        # print(f'{STDOUT_COLOR_RED}action to be taken not specified{STDOUT_COLOR_RESET}',file=sys.stderr)
        raise AttributeError('action to be taken not specified')


def call_uninstall_program(*argcs,**kwargs):
    """Actually, uninstaller"""
    raise NotImplementedError('Not implemented!')


def call_test_program(*argcs,**kwargs):
    """Only prints some test message, that helps me verify the bundle is working and is starting"""
    msg = '''
hello, world! From git-textconv-mdd setup script
    '''
    print(msg)
    return True

def call_done_program(*argcs,**kwargs):
    """Same, only prints a message - to be called when installation is finished"""
    msg = f'{STDOUT_COLOR_GREEN}Done!"{STDOUT_COLOR_RESET}'
    print(msg)
    return True

def call_printversion_program(*argcs,**kwargs):
    """Prints tool version"""
    msg = gittextconvmdd_script_version
    msg = msg.strip()
    print(msg)
    return True


run_programs = {
    'install': call_install_program,
    'uninstall': call_uninstall_program,
    'done': call_done_program,
    'test': call_test_program,
    'version': call_printversion_program,
}




def main():
    """main() here is another wrapper that calls actual function that handles this exact step, depending on value in --program param"""
    try:
        parser = argparse.ArgumentParser(
            description="git-textconv-mdd"
        )
        parser.add_argument(
            #'-1',
            '--program',
            choices=dict.keys(run_programs),
            type=str,
            required=True
        )
        args, args_rest = parser.parse_known_args()
        if args.program:
            program = '{arg}'.format(arg=args.program)
            if program in run_programs:
                run_programs[program](args_rest)
            else:
                raise AttributeError('program to run not recognized: {program}'.format(program=args.program))
        else:
            # print('{STDOUT_COLOR_RED}program to run not specified{STDOUT_COLOR_RESET}',file=sys.stderr)
            raise AttributeError('program to run not specified')
    except Exception as e:
        # the program is designed to be user-friendly
        # that's why we reformat error messages a little bit
        # stack trace is still printed (I even made it longer to 20 steps!)
        # but the error message itself is separated and printed as the last message again

        # for example, I don't write "print('File Not Found!');exit(1);", I just write "raise FileNotFoundErro()"
        print('',file=sys.stderr)
        print('Stack trace:',file=sys.stderr)
        print('',file=sys.stderr)
        traceback.print_exception(e,limit=20)
        print('',file=sys.stderr)
        print('',file=sys.stderr)
        print('',file=sys.stderr)
        print(f'{STDOUT_COLOR_RED}Error:{STDOUT_COLOR_RESET}',file=sys.stderr)
        print('',file=sys.stderr)
        print(f'{STDOUT_COLOR_RED}{e}{STDOUT_COLOR_RESET}',file=sys.stderr)
        print('',file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main()
