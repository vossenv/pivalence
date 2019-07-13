
output_dir = dist
ifeq ($(OS),Windows_NT)
	RM := rmdir /S /Q
else
	RM := rm -rf
endif

cleandir:
	-$(RM) $(output_dir)

standalone:
	pyinstaller --clean --noconfirm .build/basic.spec

wheel:
	make cleandir
	python setup.py sdist --formats=gztar  bdist_wheel

all:
	make wheel
	make standalone