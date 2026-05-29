var size_screen=window.innerWidth;
// Função para deixar o header mais transparente--> Depende do tamanho da tela --> Site inteiro
window.addEventListener('scroll',()=>{
    const header_div=document.getElementsByClassName("header_div")[0];
  
    if(size_screen>1000){

        if(window.scrollY>90){

        header_div.classList.add('solid_header_background');
       

        }
        else{

            header_div.classList.remove('solid_header_background');
           

        }


    }//Continuar quando for fazer a responsividade;
    
})

// Função para mostrar a senha do usuário --> LOGIN
function toggle_visibility(){
    const checkbox_password=window.document.getElementById("show_password");
    const password_field=window.document.getElementById("password");
    if(checkbox_password.checked){
        password_field.type="text";
    }else{
        password_field.type="password";
    }

}
