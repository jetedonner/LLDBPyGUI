#!/usr/bin/env python3

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEnginePage, QWebEngineProfile, QWebEngineSettings
# from PyQt6.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
# from PyQt6.QtWebEngineCore import
# from PyQt6.QtWebEngineCore import

import markdown

from config import *
from ui.helper.dbgOutputHelper import logDbgC




class AllowlistInterceptor(QWebEngineUrlRequestInterceptor):

	def __init__(self, parent=None, allowed_domains=None):
		super().__init__(parent)
		self.allowed_domains = allowed_domains
		logDbgC(f"self.allowed_domains: {self.allowed_domains}")

	def interceptRequest(self, info):
		url = info.requestUrl().toString()
		logDbgC(f"interceptRequest: {url}")

		if not any(domain in url for domain in self.allowed_domains):
			logDbgC(f"Blocked: {url}")
			info.block(True)
		else:
			logDbgC(f"Allowed: {url}")
			info.block(False)


class AllowAllInterceptor(QWebEngineUrlRequestInterceptor):

	def __init__(self, parent=None):
		super().__init__(parent)
		# self.allowed_domains = allowed_domains
		# logDbgC(f"self.allowed_domains: {self.allowed_domains}")

	def interceptRequest(self, info):
		info.block(False)
		pass
		# url = info.requestUrl().toString()
		# logDbgC(f"interceptRequest: {url}")
		#
		# if not any(domain in url for domain in self.allowed_domains):
		# 	logDbgC(f"Blocked: {url}")
		# 	info.block(True)
		# else:
		# 	logDbgC(f"Allowed: {url}")


class CreditsDialog(QDialog):

	allowed = ["kimhauser.ch",
			   	"jetedonner.github.io",
				"https://fonts.googleapis.com/css2?family=Lato&family=Source+Sans+Pro:wght@400;600;700;900&display=swap",
				"https://cdn.jsdelivr.net/npm/bootstrap@4/dist/css/bootstrap.min.css",
				"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/css/all.min.css",
				"https://cdn.jsdelivr.net/npm/jquery@3/dist/jquery.min.js",
				"https://cdn.jsdelivr.net/npm/simple-jekyll-search@1.10.0/dest/simple-jekyll-search.min.js",
				"https://cdn.jsdelivr.net/combine/npm/dayjs@1/dayjs.min.js,npm/dayjs@1/locale/de-ch.min.js,npm/dayjs@1/plugin/relativeTime.min.js,npm/dayjs@1/plugin/localizedFormat.min.js",
				"https://cdn.jsdelivr.net/npm/bootstrap@4/dist/js/bootstrap.bundle.min.js",
				"https://www.googletagmanager.com/gtag/js?id=G-59J4B01J7D",
				"https://fonts.gstatic.com/s/sourcesanspro/v22/6xKydSBYKcSV-LCoeQqfX1RYOo3iu4nwlxdu3cOWxw.woff2",
				"https://fonts.gstatic.com/s/sourcesanspro/v22/6xK3dSBYKcSV-LCoeQqfX1RYOo3qOK7lujVj9w.woff2",
				"https://fonts.gstatic.com/s/sourcesanspro/v22/6xKydSBYKcSV-LCoeQqfX1RYOo3i54rwlxdu3cOWxw.woff2",
				"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-brands-400.woff2",
				"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-solid-900.woff2",
				"https://fonts.gstatic.com/s/lato/v24/S6uyw4BMUTPHjx4wXiWtFCc.woff2",
				"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-regular-400.woff2",
				"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-brands-400.woff",
				"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-solid-900.woff",
				"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-regular-400.woff",
				"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-brands-400.ttf",
				"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-solid-900.ttf",
				"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-regular-400.ttf",
				"https://cdn.jsdelivr.net/gh/afeld/bootstrap-toc@1.0.1/dist/bootstrap-toc.min.js",
			   "https://cdn.jsdelivr.net/gh/afeld/bootstrap-toc@1.0.1/dist/bootstrap-toc.min.css",
			   "https://cdn.jsdelivr.net/npm/magnific-popup@1/dist/magnific-popup.min.css",
				"https://cdn.jsdelivr.net/gh/afeld/bootstrap-toc@1.0.1/dist/bootstrap-toc.min.css",
				"https://cdn.jsdelivr.net/npm/magnific-popup@1/dist/magnific-popup.min.css",
				"https://cdn.jsdelivr.net/gh/afeld/bootstrap-toc@1.0.1/dist/bootstrap-toc.min.js",
				"https://cdn.jsdelivr.net/combine/npm/magnific-popup@1/dist/jquery.magnific-popup.min.js,npm/lozad/dist/lozad.min.js,npm/clipboard@2/dist/clipboard.min.js",
				"https://www.youtube.com",
			   	"https://rr2---sn-n0ogpnx-1gis.googlevideo.com",
			   "youtube.com",
			   "www.youtube.com",
			   "youtu.be",
			   "googlevideo.com",  # video stream CDN
			   "ytimg.com",  # thumbnails and assets
			   "gstatic.com",  # fonts and scripts
			   "google.com",  # account and auth
			   "accounts.google.com",
			   "doubleclick.net",  # ads
			   "youtube-nocookie.com",
			   "region1.google-analytics.com"
	]
	profile = None
	interceptor = None
	page = None
	profileReadme = None
	interceptorReadme = None
	pageReadme = None

	viewReadme =None
	viewGithubPages = None

	def __init__(self, title="", prompt=""):
		super().__init__()

		# print("ELLO")

		self.allowed = None
		self.profile = None
		self.interceptor = None
		self.page = None
		self.profileReadme = None
		self.interceptorReadme = None
		self.pageReadme = None

		self.viewReadme = None
		self.viewGithubPages = None

		self.allowed = ["kimhauser.ch",
					"jetedonner.github.io",
					"https://fonts.googleapis.com/css2?family=Lato&family=Source+Sans+Pro:wght@400;600;700;900&display=swap",
					"https://cdn.jsdelivr.net/npm/bootstrap@4/dist/css/bootstrap.min.css",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/css/all.min.css",
					"https://cdn.jsdelivr.net/npm/jquery@3/dist/jquery.min.js",
					"https://cdn.jsdelivr.net/npm/simple-jekyll-search@1.10.0/dest/simple-jekyll-search.min.js",
					"https://cdn.jsdelivr.net/combine/npm/dayjs@1/dayjs.min.js,npm/dayjs@1/locale/de-ch.min.js,npm/dayjs@1/plugin/relativeTime.min.js,npm/dayjs@1/plugin/localizedFormat.min.js",
					"https://cdn.jsdelivr.net/npm/bootstrap@4/dist/js/bootstrap.bundle.min.js",
					"https://www.googletagmanager.com/gtag/js?id=G-59J4B01J7D",
					"https://fonts.gstatic.com/s/sourcesanspro/v22/6xKydSBYKcSV-LCoeQqfX1RYOo3iu4nwlxdu3cOWxw.woff2",
					"https://fonts.gstatic.com/s/sourcesanspro/v22/6xK3dSBYKcSV-LCoeQqfX1RYOo3qOK7lujVj9w.woff2",
					"https://fonts.gstatic.com/s/sourcesanspro/v22/6xKydSBYKcSV-LCoeQqfX1RYOo3i54rwlxdu3cOWxw.woff2",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-brands-400.woff2",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-solid-900.woff2",
					"https://fonts.gstatic.com/s/lato/v24/S6uyw4BMUTPHjx4wXiWtFCc.woff2",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-regular-400.woff2",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-brands-400.woff",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-solid-900.woff",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-regular-400.woff",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-brands-400.ttf",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-solid-900.ttf",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.11.2/webfonts/fa-regular-400.ttf",
					"https://cdn.jsdelivr.net/gh/afeld/bootstrap-toc@1.0.1/dist/bootstrap-toc.min.js",
				   "https://cdn.jsdelivr.net/gh/afeld/bootstrap-toc@1.0.1/dist/bootstrap-toc.min.css",
				   "https://cdn.jsdelivr.net/npm/magnific-popup@1/dist/magnific-popup.min.css",
					"https://cdn.jsdelivr.net/gh/afeld/bootstrap-toc@1.0.1/dist/bootstrap-toc.min.css",
					"https://cdn.jsdelivr.net/npm/magnific-popup@1/dist/magnific-popup.min.css",
					"https://cdn.jsdelivr.net/gh/afeld/bootstrap-toc@1.0.1/dist/bootstrap-toc.min.js",
					"https://cdn.jsdelivr.net/combine/npm/magnific-popup@1/dist/jquery.magnific-popup.min.js,npm/lozad/dist/lozad.min.js,npm/clipboard@2/dist/clipboard.min.js",
					"https://www.youtube.com",
			   		"https://rr2---sn-n0ogpnx-1gis.googlevideo.com",
				   "youtube.com",
				   "www.youtube.com",
				   "youtu.be",
				   "googlevideo.com",  # video stream CDN
				   "ytimg.com",  # thumbnails and assets
				   "gstatic.com",  # fonts and scripts
				   "google.com",  # account and auth
				   "accounts.google.com",
				   "doubleclick.net",  # ads
				   "youtube-nocookie.com",
				   "region1.google-analytics.com"]

		self.setWindowTitle(title)

		QBtn = QDialogButtonBox.StandardButton.Ok  # | QDialogButtonBox.StandardButton.Cancel

		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		# self.buttonBox.rejected.connect(self.reject)

		self.wdtInner = QWidget()
		self.layoutMain = QHBoxLayout()
		self.layout = QVBoxLayout()
		self.layoutImg = QVBoxLayout()
		self.image_label = QLabel()
		self.image_label.setPixmap(ConfigClass.pixBugGreen)

		# Add label to layout

		self.message = QLabel(prompt)
		self.layoutImg.addWidget(self.image_label)
		self.spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Fixed,
								  QSizePolicy.Policy.Expanding)  # Adjust spacer size as needed
		self.layoutImg.addItem(self.spacer)
		self.wdtImg = QWidget()
		self.wdtImg.setLayout(self.layoutImg)
		self.layoutMain.addWidget(self.wdtImg)
		self.layout.addWidget(self.message)
		self.wdtInner.setLayout(self.layout)
		self.wdtInner.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
		self.layoutMain.addWidget(self.wdtInner)
		self.setLayout(self.layoutMain)

		self.resize(800, 600)

		self.viewReadme = QWebEngineView()
		self.viewReadme.setHtml(self.loadMD("README.md"))

		self.viewGithubPages = QWebEngineView()
		self.setAllowedURLs()

		self.viewCredits = QWebEngineView()
		self.viewCredits.setHtml(self.loadMD("CREDITS.md"))

		self.viewLicense = QWebEngineView()
		self.viewLicense.setHtml(self.loadMD("LICENSE.md"))

		self.window = QWidget()
		self.window.setWindowTitle("About / Infos")
		self.layout2 = QVBoxLayout()

		self.tabs = QTabWidget()
		self.tabs.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
		# First tab
		self.tab1 = QWidget()
		self.tab1_layout = QVBoxLayout()
		self.tab1_layout.addWidget(self.viewReadme)
		self.tab1.setLayout(self.tab1_layout)

		self.tab4 = QWidget()
		self.tab4_layout = QVBoxLayout()
		self.tab4_layout.addWidget(self.viewGithubPages)
		self.tab4.setLayout(self.tab4_layout)

		# Second tab
		self.tab2 = QWidget()
		self.tab2_layout = QVBoxLayout()
		self.tab2_layout.addWidget(self.viewCredits)
		self.tab2.setLayout(self.tab2_layout)

		self.tab3 = QWidget()
		self.tab3_layout = QVBoxLayout()
		self.tab3_layout.addWidget(self.viewLicense)
		self.tab3.setLayout(self.tab3_layout)

		self.tabs.addTab(self.tab1, "Readme")
		self.tabs.addTab(self.tab4, "Github Pages")
		self.tabs.addTab(self.tab2, "Credits")
		self.tabs.addTab(self.tab3, "License")

		self.layout2.addWidget(self.tabs)
		self.window.setLayout(self.layout2)

		self.layout.addWidget(self.window)

		self.lblAuthor = QLabel(f"Author: Kim-David Hauser, kim@kimhauser.ch")
		self.layout.addWidget(self.lblAuthor)

		self.layout.addWidget(self.buttonBox)

		self.viewGithubPages.load(QUrl(ConfigClass.githubPagesURL))

	def setAllowedURLs(self):
		id = 0
		self.profile = QWebEngineProfile(f"storage-{id}", self.viewGithubPages) # QWebEngineProfile.defaultProfile()
		self.interceptor = AllowlistInterceptor(self, self.allowed)

		self.profile.setUrlRequestInterceptor(self.interceptor)

		# view = self.viewGithubPages #QWebEngineView()
		self.page = QWebEnginePage(self.profile, self.viewGithubPages)
		self.page.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
		self.page.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
		self.viewGithubPages.setPage(self.page)

		# self.profileReadme = QWebEngineProfile(f"storage-{id}", self.viewGithubPages) # QWebEngineProfile.defaultProfile()
		# self.interceptorReadme = AllowAllInterceptor(self)
		#
		# self.profileReadme.setUrlRequestInterceptor(self.interceptorReadme)
		# self.pageReadme = QWebEnginePage(self.profileReadme, self.viewReadme)
		# # self.pageReadme.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
		# # self.pageReadme.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
		# self.pageReadme.setHtml(self.loadMD("README.md"))
		# self.viewReadme.setPage(self.pageReadme)
		# self.viewReadme.setPage(self.page)
		# self.viewReadme.setHtml(self.loadMD("README.md"))

		# view.load(QUrl("https://example.com"))

	def loadMD(self, fileName):
		script_dir = os.path.dirname(os.path.abspath(__file__))
		md_path = os.path.join(script_dir + "/../../", fileName)

		# Read the Markdown file content
		with open(md_path, "r", encoding="utf-8") as f:
			md_text = f.read()

		return markdown.markdown(md_text, extensions=["fenced_code", "tables"])
