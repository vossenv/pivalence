
# -*- mode: python -*-

block_cipher = None

# noinspection PyUnresolvedReferences
a = Analysis(['../piveilance/app.py'],
             pathex=[],
             binaries=[( '../piveilance/resources/Qt5Core.dll', 'PyQt5/Qt/bin')],
             datas=  [( '../piveilance/resources', 'resources' )],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# noinspection PyUnresolvedReferences
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

# noinspection PyUnresolvedReferences
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          exclude_binaries=False,
          name='piVeilence',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='../piveilance/resources/icon.ico' )
