import sys
import os
import shutil
import colorama
import clr
from difflib import unified_diff
from colorama import Fore, Back, Style, init

clr.AddReference('xltrail-core')
from xltrail.core import Workbook 


if __name__ == '__main__':
    if not 8 <= len(sys.argv) <= 9:
        print('Unexpected number of arguments')
        sys.exit(0)

    if len(sys.argv) == 8:
        _, workbook_name, workbook_b, _, _, workbook_a, _ , _ = sys.argv
        numlines = 3
    if len(sys.argv) == 9:
        _, numlines, workbook_name, workbook_b, _, _, workbook_a, _, _ = sys.argv
        numlines = int(numlines)

    path_workbook_a = os.path.abspath(workbook_a)
    path_workbook_b = os.path.abspath(workbook_b)

    workbook_a = Workbook(path_workbook_a)
    workbook_b = Workbook(path_workbook_b)

    workbook_a_modules = dict([(m.name, m) for m in workbook_a.vba_modules])
    workbook_b_modules = {} if workbook_b == 'nul' else dict([(m.name, m) for m in workbook_b.vba_modules])

    diffs = []
    for module_a, vba_a in workbook_a_modules.items():
        if module_a not in workbook_b_modules:
            diffs.append({
                'a': '--- /dev/null',
                'b': '+++ b/' + workbook_name + '/VBA/' + vba_a.type + '/' + module_a,
                'diff': '\n'.join([Fore.GREEN + '+' + line for line in vba_a.split('\n')])
            })
        elif vba_a.digest != workbook_b_modules[module_a].digest:
            diffs.append({
                'a': '--- a/' + workbook_name + '/VBA/' + vba_a.type + '/' + module_a,
                'b': '+++ b/' + workbook_name + '/VBA/' + vba_a.type + '/' + module_a,
                'diff': '\n'.join([(Fore.RED if line.startswith('-') else (Fore.GREEN if line.startswith('+') else (Fore.CYAN if line.startswith('@') else ''))) + line.strip('\n') for line in list(unified_diff(workbook_b_modules[module_a].content.split('\n'), vba_a.content.split('\n'), n=numlines))[2:]])
            })

    for module_b, vba_b in workbook_b_modules.items():
        if module_b not in workbook_a_modules:
            diffs.append({
                'a': '--- b/' + workbook_name + '/VBA/' + vba_b.type + '/' + module_b,
                'b': '+++ /dev/null',
                'diff': '\n'.join([Fore.RED + '-' + line for line in vba_b.content.split('\n')])
            })


    colorama.init(strip=False)

    print(Style.BRIGHT + 'diff --xltrail ' + 'a/' + workbook_name + ' b/' + workbook_name)
    for diff in diffs:
        print(Style.BRIGHT + diff['a'])
        print(Style.BRIGHT + diff['b'])
        print(diff['diff'])
        print('')
