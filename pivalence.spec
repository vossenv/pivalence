# -*- mode: python -*-

block_cipher = None

a = Analysis(['pivalence/pivalence.py'],
             pathex=[],
             binaries=[( 'pivalence/resources/Qt5Core.dll', 'PyQt5/Qt/bin')],
             datas=  [( 'pivalence/resources/*.jpg', 'resources' ),
                      ( 'pivalence/resources/*.png', 'resources' ),
                      ( 'pivalence/resources/*.qss', 'resources' )],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          exclude_binaries=False,
          name='piValence',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='.build/usticon.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='pivalence')
