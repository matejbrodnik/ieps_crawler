// Get HTML head element 
// localStorage.setItem('design_packs_key', 'dfghdgfjfh');


console.log('Using theme sections by Design Packs 🎒 | learn more at https://design-packs.com')


window.addEventListener('shopify:section:load', function (e) {
	const sectionJS = document.querySelector(`[data-dsgn-pck-js="${e.detail.sectionId}"]`);
	const sectionExternalJS = document.querySelector(`[data-dsgn-pck-external-js="${e.detail.sectionId}"]`);
	const section = document.querySelector(`#DP--${e.detail.sectionId}`);

	const loadJavaScriptBlock = () => {
		if (sectionJS) {
			const sectionScript = sectionJS.innerHTML;
			const newScript = document.createElement('script');
			const inlineScript = document.createTextNode(sectionScript);
			newScript.appendChild(inlineScript);
			section.appendChild(newScript);
		}
	}

	if (sectionExternalJS) {
		const newScript = document.createElement('script');
		const externalPath = sectionExternalJS.src;
		newScript.src = externalPath;
		section.appendChild(newScript);
		newScript.onload = () => {
			loadJavaScriptBlock();
		}
	} else {
		loadJavaScriptBlock();
	}

});
