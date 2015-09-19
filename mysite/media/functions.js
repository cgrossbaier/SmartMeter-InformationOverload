
function get_text_from_id(text_array, id) {
	return text_array[id];
}

function check_elements(elements) {
	if (elements.length > 1) {
		value = "";
		for (var j = 0; j < elements.length; j++) {
			if (elements[j].checked == true) {
				value = elements[j].value;
			}
		}			
		if (value == "") {
			return false;
		}
	}
	if (elements.length == 1) {
		if (elements[0].value == "") {
			return false;
		}
	}
	return true;
}

function check_complete(question_array, form) {
	for (var i = 0; i < question_array.length; i++) {
		elms = document.getElementsByName(form + "_" + question_array[i]);
		if (check_elements(elms) == false) {
			return i;
		}
		elms = document.getElementsByName(form + "_secondary_" + question_array[i]);
		if (check_elements(elms) == false) {
			return i;
		}
	}
	return true;
}