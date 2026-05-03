function typesetAnswer(inputId, outputId) {
    var inputIdVal = document.getElementById(inputId).value;
    document.getElementById(outputId).innerText = inputIdVal;
    MathJax.typeset([document.getElementById(outputId)]);
}

function toggleDiv(elementId, style) {
    var element = document.getElementById(elementId);

    if (element.style.display === 'none') {
        element.style.display = style;
    } else {
        element.style.display = 'none';
    }
}
