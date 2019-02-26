///////////////////////////////////////////////////////////////////////////
// C++ code generated with wxFormBuilder (version Jun 17 2015)
// http://www.wxformbuilder.org/
//
// PLEASE DO "NOT" EDIT THIS FILE!
///////////////////////////////////////////////////////////////////////////

#include "noname.h"

///////////////////////////////////////////////////////////////////////////

MyFrame2::MyFrame2( wxWindow* parent, wxWindowID id, const wxString& title, const wxPoint& pos, const wxSize& size, long style ) : wxFrame( parent, id, title, pos, size, style )
{
	this->SetSizeHints( wxDefaultSize, wxDefaultSize );
	
	m_menubar1 = new wxMenuBar( 0 );
	m_menu1 = new wxMenu();
	m_menu11 = new wxMenu();
	wxMenuItem* m_menu11Item = new wxMenuItem( m_menu1, wxID_ANY, wxT("MyMenu"), wxEmptyString, wxITEM_NORMAL, m_menu11 );
	wxMenuItem* m_menuItem1;
	m_menuItem1 = new wxMenuItem( m_menu11, wxID_ANY, wxString( wxT("MyMenuItem") ) , wxEmptyString, wxITEM_NORMAL );
	m_menu11->Append( m_menuItem1 );
	
	m_menu1->Append( m_menu11Item );
	
	m_menu21 = new wxMenu();
	wxMenuItem* m_menu21Item = new wxMenuItem( m_menu1, wxID_ANY, wxT("MyMenu"), wxEmptyString, wxITEM_NORMAL, m_menu21 );
	wxMenuItem* m_menuItem2;
	m_menuItem2 = new wxMenuItem( m_menu21, wxID_ANY, wxString( wxT("MyMenuItem") ) , wxEmptyString, wxITEM_NORMAL );
	m_menu21->Append( m_menuItem2 );
	
	m_menu1->Append( m_menu21Item );
	
	m_menubar1->Append( m_menu1, wxT("文件(&F)") ); 
	
	m_menu2 = new wxMenu();
	m_menubar1->Append( m_menu2, wxT("编辑(&E)") ); 
	
	m_menu3 = new wxMenu();
	m_menubar1->Append( m_menu3, wxT("格式(&O)") ); 
	
	m_menu4 = new wxMenu();
	m_menubar1->Append( m_menu4, wxT("查看(&V)") ); 
	
	m_menu5 = new wxMenu();
	m_menubar1->Append( m_menu5, wxT("帮助(&H)") ); 
	
	this->SetMenuBar( m_menubar1 );
	
	wxGridBagSizer* gbSizer1;
	gbSizer1 = new wxGridBagSizer( 0, 0 );
	gbSizer1->SetFlexibleDirection( wxBOTH );
	gbSizer1->SetNonFlexibleGrowMode( wxFLEX_GROWMODE_SPECIFIED );
	
	m_auiToolBar2 = new wxAuiToolBar( this, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxAUI_TB_HORZ_LAYOUT ); 
	m_tool6 = m_auiToolBar2->AddTool( wxID_ANY, wxT("tool"), wxBitmap( wxT("../save_16.png"), wxBITMAP_TYPE_ANY ), wxNullBitmap, wxITEM_NORMAL, wxEmptyString, wxEmptyString, NULL ); 
	
	m_tool7 = m_auiToolBar2->AddTool( wxID_ANY, wxT("tool"), wxBitmap( wxT("../clear.png"), wxBITMAP_TYPE_ANY ), wxNullBitmap, wxITEM_NORMAL, wxEmptyString, wxEmptyString, NULL ); 
	
	m_tool8 = m_auiToolBar2->AddTool( wxID_ANY, wxT("tool"), wxBitmap( wxT("../left.png"), wxBITMAP_TYPE_ANY ), wxNullBitmap, wxITEM_NORMAL, wxEmptyString, wxEmptyString, NULL ); 
	
	m_tool9 = m_auiToolBar2->AddTool( wxID_ANY, wxT("tool"), wxBitmap( wxT("../center.png"), wxBITMAP_TYPE_ANY ), wxNullBitmap, wxITEM_NORMAL, wxEmptyString, wxEmptyString, NULL ); 
	
	m_tool10 = m_auiToolBar2->AddTool( wxID_ANY, wxT("tool"), wxBitmap( wxT("../right.png"), wxBITMAP_TYPE_ANY ), wxNullBitmap, wxITEM_NORMAL, wxEmptyString, wxEmptyString, NULL ); 
	
	m_auiToolBar2->Realize(); 
	
	gbSizer1->Add( m_auiToolBar2, wxGBPosition( 0, 0 ), wxGBSpan( 1, 1 ), wxALL, 5 );
	
	
	this->SetSizer( gbSizer1 );
	this->Layout();
	m_statusBar1 = this->CreateStatusBar( 1, wxST_SIZEGRIP, wxID_ANY );
	
	this->Centre( wxBOTH );
}

MyFrame2::~MyFrame2()
{
}
