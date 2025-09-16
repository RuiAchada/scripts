const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");
const fs = require("fs");
const axios = require("axios");
const { exec } = require("child_process");

puppeteer.use(StealthPlugin());

async function loadSettings(filePath = "settings.json") {
	const data = fs.readFileSync(filePath, "utf-8");
	return JSON.parse(data);
}

async function delay(time) {
	return new Promise(function (resolve) {
		setTimeout(resolve, time);
	});
}

async function getM3u8Url(websiteUrl, buttonClassName) {
	let browser;
	try {
		console.log(`Opening the website: ${websiteUrl}`);

		browser = await puppeteer.launch({
			headless: false, // Run in headful mode to see the browser in action
			args: ["--no-sandbox", "--disable-setuid-sandbox"],
		});

		const page = await browser.newPage();

		// Handle the "Leave site?" dialog
		page.on("dialog", async (dialog) => {
			console.log(`Dialog detected: ${dialog.message()}`);
			// Automatically click the "Cancel" button
			await dialog.dismiss();
		});

		// Inject bypass scripts to override detection and disable event listeners
		await page.evaluateOnNewDocument(() => {
			// Override the DevTools detection methods
			window.isDevToolOpened = () => false;
			window.markDevToolOpenState = () => {};

			// Disable interval and timeout-based detection
			window.registInterval = function () {};
			window.clearDDInterval = function () {};
			window.clearDDTimeout = function () {};

			// Prevent event listeners for disabling keys, context menus, and interactions
			window.addEventListener = function () {};

			// Override or nullify callbacks that close the window on DevTools open
			window.config = {
				...window.config,
				ondevtoolopen: null,
				ondevtoolclose: null,
				clearIntervalWhenDevOpenTrigger: false,
			};

			// Modify navigator properties to evade detection
			Object.defineProperty(navigator, "webdriver", { get: () => false });
			Object.defineProperty(navigator, "plugins", { get: () => [1, 2, 3] });
			Object.defineProperty(navigator, "languages", {
				get: () => ["en-US", "en"],
			});

			// Prevent page redirection or other interruptions
			window.onbeforeunload = () => true;
		});

		await page.goto(websiteUrl, { waitUntil: "networkidle2" });

		// Save the initial page source to check if the page loaded correctly
		const pageSourceInitial = await page.content();
		fs.writeFileSync("page_source_initial.html", pageSourceInitial);

		console.log("Waiting for the play button...");
		await page.waitForSelector(`.${buttonClassName}`, { visible: true });

		// Save the page source just before clicking the play button
		const pageSourceBeforeClick = await page.content();
		fs.writeFileSync("page_source_before_click.html", pageSourceBeforeClick);

		// Simulate human-like interaction with a random delay
		const delayTime = 5000 + Math.floor(Math.random() * 5000);
		console.log(`Delaying for ${delayTime} milliseconds before interacting...`);
		await delay(delayTime);

		const playButton = await page.$(`.${buttonClassName}`);
		await playButton.click();

		console.log("Play button clicked, waiting for m3u8 URL to load...");
		await delay(10000); // Wait for 10 seconds

		// Save the page source after the button click
		const pageSourceAfterClick = await page.content();
		fs.writeFileSync("page_source_after_click.html", pageSourceAfterClick);

		// Capture network requests
		let m3u8Url = null;
		page.on("response", async (response) => {
			const url = response.url();
			if (url.endsWith(".m3u8")) {
				m3u8Url = url;
			}
		});

		// Wait a bit to ensure network requests are captured
		await delay(5000);

		if (m3u8Url) {
			console.log(`m3u8 URL found: ${m3u8Url}`);
		} else {
			console.error("m3u8 URL not found.");
		}

		await browser.close();
		return m3u8Url;
	} catch (error) {
		console.error(
			`An error occurred while fetching the m3u8 URL: ${error.message}`,
		);
		if (browser) {
			await browser.close();
		}
		return null;
	}
}

async function fetchHeaders(url) {
	try {
		console.log(`Fetching headers from ${url}`);
		const response = await axios.get(url);
		return response.headers;
	} catch (error) {
		console.error(`An error occurred while fetching headers: ${error.message}`);
		return null;
	}
}

function downloadHlsStream(manifestUrl, headers, outputFilename) {
	const ffmpegCommand = [
		"ffmpeg",
		"-headers",
		Object.entries(headers)
			.map(([key, value]) => `${key}: ${value}`)
			.join("\r\n"),
		"-i",
		manifestUrl,
		"-c",
		"copy",
		outputFilename,
	].join(" ");

	console.log(`Starting download from ${manifestUrl}`);
	exec(ffmpegCommand, (error, stdout, stderr) => {
		if (error) {
			console.error(
				`An error occurred while downloading the video: ${error.message}`,
			);
			return;
		}
		console.log(`Video downloaded successfully and saved as ${outputFilename}`);
	});
}

(async () => {
	const settings = await loadSettings();

	const websiteUrl = settings.website_url;
	const outputFilename = settings.output_filename;
	const buttonClassName = settings.button_class_name;

	if (!websiteUrl) {
		console.error("The website URL cannot be empty.");
		return;
	} else if (!outputFilename) {
		console.error("The output filename cannot be empty.");
		return;
	}

	// Step 1: Get the m3u8 URL by automating the browser
	const manifestUrl = await getM3u8Url(websiteUrl, buttonClassName);

	if (manifestUrl) {
		// Step 2: Fetch headers dynamically from the website
		const headers = await fetchHeaders(websiteUrl);
		if (headers) {
			// Step 3: Download the video stream using the m3u8 URL and headers
			downloadHlsStream(manifestUrl, headers, outputFilename);
		} else {
			console.error(
				"Failed to fetch headers, cannot proceed with the download.",
			);
		}
	} else {
		console.error(
			"Failed to retrieve the m3u8 URL, cannot proceed with the download.",
		);
	}
})();
