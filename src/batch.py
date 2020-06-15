import wireviz
import os

demos     = 0 # 2
examples  = 0 # 6
tutorials = 7 # 7

if demos:
    for i in range(1,demos+1):
        fn = '../examples/demo{:02d}.yml'.format(i)
        print(fn)
        wireviz.parse(fn, gen_bom=True)

if examples:
    with open(os.path.abspath('../examples/readme.md'), 'w') as file:
        file.write('# Example gallery\n')
        for i in range(1,examples+1):
            fn = '../examples/ex{:02d}.yml'.format(i)
            print(fn)
            wireviz.parse(fn, gen_bom=True)

            file.write('## Example {:02d}\n'.format(i))
            file.write('![](ex{:02d}.png)\n\n'.format(i))
            file.write('[Source](ex{:02d}.yml) - [Bill of Materials](ex{:02d}.bom.tsv)\n\n\n'.format(i,i))

if tutorials:
    with open(os.path.abspath('../tutorial/readme.md'), 'w') as file:
        file.write('# WireViz Tutorial\n')
        for i in range(1,tutorials+1):
            fn = '../tutorial/tutorial{:02d}.yml'.format(i)
            print(fn)
            wireviz.parse(fn, gen_bom=True)

            with open(os.path.abspath('../tutorial/tutorial{:02d}.md'.format(i)), 'r') as info:
                for line in info:
                    file.write('{}'.format(line))
            file.write('\n[Source](tutorial{:02d}.yml):\n\n'.format(i))

            with open(os.path.abspath('../tutorial/tutorial{:02d}.yml'.format(i)), 'r') as src:
                for line in src:
                    file.write('    {}'.format(line))
            file.write('\n')

            file.write('\nOutput:\n\n'.format(i))

            file.write('![](tutorial{:02d}.png)\n\n'.format(i))

            # file.write('[Bill of Materials](tutorial{:02d}.bom.tsv)\n\n\n'.format(i))
