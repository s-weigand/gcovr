
all:
	mkdir -p build1 build2
	cd build1 ; $(CXX) -fprofile-arcs -ftest-coverage -fPIC ../main.c -o testcase
	cd build2 ; $(CXX) -fprofile-arcs -ftest-coverage -fPIC -DFOO_OTHER_LINE ../main.c -o testcase

run: txt cobertura html sonarqube coveralls

coverage.json:
	cd build1 ; ./testcase
	cd build2 ; ./testcase
	$(GCOVR) --verbose --merge-mode-functions=merge-use-line-max --json-pretty --json coverage.json

txt: coverage.json
	$(GCOVR) -a $< -o coverage.txt

cobertura: coverage.json
	$(GCOVR) -a $< --cobertura-pretty --cobertura cobertura.xml

html: coverage.json
	$(GCOVR) -a $< --html-details -o coverage.html

coveralls: coverage.json
	$(GCOVR) -a $<  --coveralls-pretty --coveralls coveralls.json

sonarqube: coverage.json
	$(GCOVR) -a $< --sonarqube -o sonarqube.xml

clean:
	rm -rf build1 build2
	rm -f *.gc* coverage*.* cobertura*.* sonarqube*.* coveralls.json
