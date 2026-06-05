APP_NAME=MarkItDownStudio
SWIFT_FILES=$(wildcard Sources/*.swift)

all: app

app:
	@echo "Building $(APP_NAME).app..."
	@mkdir -p "$(APP_NAME).app/Contents/MacOS"
	@mkdir -p "$(APP_NAME).app/Contents/Resources"
	@echo "Compiling Swift sources..."
	@swiftc $(SWIFT_FILES) -o "$(APP_NAME).app/Contents/MacOS/$(APP_NAME)"
	@echo "Copying Info.plist..."
	@cp Info.plist "$(APP_NAME).app/Contents/Info.plist"
	@echo "Done!"

clean:
	@rm -rf "$(APP_NAME).app"
