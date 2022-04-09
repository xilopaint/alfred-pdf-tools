build_workflow:
	@ echo "Creating binary..."
	@ pyinstaller alfred_pdf_tools.spec
	@ echo "Building workflow..."
	@ zip alfred_pdf_tools -r -j dist/alfred_pdf_tools; cd src; zip ../alfred_pdf_tools -r * -x alfred_pdf_tools* workflow/.*; cd ..
	@ mv alfred_pdf_tools.zip "Alfred PDF Tools.alfredworkflow"
	@ echo "Finished."