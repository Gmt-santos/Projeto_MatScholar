var size_screen=window.innerWidth;
// Função para deixar o header mais transparente--> Depende do tamanho da tela
window.addEventListener('scroll',()=>{
    const header_div=document.getElementsByClassName("header_div")[0];
    const header_buttons=document.getElementsByClassName("index_login_button_a")[0];
    if(size_screen>1000){

        if(window.scrollY>90){

        header_div.classList.add('solid_header_background');
        header_buttons.classList.add("solid_header_buttons");

        }
        else{

            header_div.classList.remove('solid_header_background');
            header_buttons.classList.remove("solid_header_buttons");

        }


    }//Continuar quando for fazer a responsividade;
    
})