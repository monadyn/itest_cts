pushd N:\[iTest]\iTest
del /s /q build\*.*
del /s /q dist\*.*
del /s /q iTest.egg-info\*.*
echo C:\Python27\python setup.py install 

echo hello
C:\Python27\python setup.py bdist_egg


xcopy /y dist\iTest-1.0-py2.7.egg D:\site\trac\plugins
pause
