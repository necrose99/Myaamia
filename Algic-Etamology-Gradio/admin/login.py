# ./Admin/login.py
import os
import ssl
from flask import Blueprint, redirect, url_for, request, session, flash, render_template_string
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_login_saml import FlaskSAML
from authlib.integrations.flask_client import OAuth
import ldap3
from ldap3 import Server, Connection, NTLM, Tls, ALL

from Admin.cfg import ADConfig  # Stores AD_SERVER, AD_DOMAIN, AD_BASE_DN, ADCS_ROOT_CA_PATH

# Isolated Blueprint Routing Space
auth_bp = Blueprint('auth_portal', __name__, template_folder='templates')

# Protocol Adapters Initialization
saml_adapter = FlaskSAML(prefix='SSO')
oauth_client = OAuth()

# -------------------------------------------------------------------
# A. UNIFIED USER PRINCIPAL OBJECT
# -------------------------------------------------------------------
class AuthenticatedLinguist(UserMixin):
    """
    Agnoistic security context housing identity assertions across 
    Active Directory, SAML, and Social OAuth layers.
    """
    def __init__(self, user_id, display_name, email, role="researcher", provider="local"):
        self.id = user_id
        self.display_name = display_name
        self.email = email
        self.role = role          # Escalation flags: 'admin' vs 'researcher'
        self.provider = provider  # Source tracking: 'ad', 'saml', 'google'

# -------------------------------------------------------------------
# B. BLUEPRINT CONFIGURATION REGISTRATION HOOK
# -------------------------------------------------------------------
@auth_bp.record_once
def on_blueprint_registration(state):
    """Initializes multi-protocol handshakes during Flask context assembly."""
    app = state.app
    
    # Configure SAML Settings
    app.config.setdefault('SSO_METADATA_URL', os.environ.get('SSO_METADATA_URL', 'https://<idp>/protocol/saml/descriptor'))
    saml_adapter.init_app(app)
    
    # Configure Social Identity provider (Google Auth)
    oauth_client.init_app(app)
    oauth_client.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID', 'placeholder-id'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', 'placeholder-secret'),
        server_metadata_url='https://google.com',
        client_kwargs={'scope': 'openid email profile'}
    )

# -------------------------------------------------------------------
# C. UNIVERSITY ACTIVE DIRECTORY HANDLER (LDAP3 + ADCS)
# -------------------------------------------------------------------
def verify_university_ad_credentials(username, password):
    """
    Authenticates university staff via secure NTLM domain binding,
    verifying SSL handshake integrity against the ADCS CA chain.
    """
    try:
        # Enforce server authentication via the university root certificate authority
        tls_config = Tls(
            validate=ssl.CERT_REQUIRED,
            version=ssl.PROTOCOL_TLSv1_2,
            ca_certs_file=ADConfig.ADCS_ROOT_CA_PATH
        )
        
        server = Server(ADConfig.AD_SERVER, use_ssl=True, tls=tls_config, get_info=ALL)
        bind_user = f"{ADConfig.AD_DOMAIN}\\{username}"
        
        conn = Connection(
            server, 
            user=bind_user, 
            password=password, 
            authentication=NTLM, 
            raise_exceptions=True
        )
        
        if conn.bind():
            search_filter = f"(sAMAccountName={username})"
            conn.search(
                search_base=ADConfig.AD_BASE_DN, 
                search_filter=search_filter, 
                attributes=['displayName', 'mail', 'memberOf']
            )
            
            if conn.entries:
                ad_entry = conn.entries[0]
                
                # Check for administrative security groups
                user_groups = str(ad_entry.memberOf) if hasattr(ad_entry, 'memberOf') else ""
                role = "admin" if "Linguistics-Admins" in user_groups else "researcher"
                
                return AuthenticatedLinguist(
                    user_id=username,
                    display_name=str(ad_entry.displayName) if hasattr(ad_entry, 'displayName') else username,
                    email=str(ad_entry.mail) if hasattr(ad_entry, 'mail') else "",
                    role=role,
                    provider="ad"
                )
    except ldap3.core.exceptions.LDAPException as e:
        print(f"🔒 Secure Active Directory Authentication Failure: {str(e)}")
        return None
    finally:
        if 'conn' in locals() and conn.bound:
            conn.unbind()
    return None

# -------------------------------------------------------------------
# D. GRAPH PORTAL ROUTING CONTEXT
# -------------------------------------------------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def universal_login():
    """Renders single entry view mapping all active identity paths."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Default local/institutional authentication vector via Active Directory
        user = verify_university_ad_credentials(username, password)
        if user:
            login_user(user)
            # Store metadata states directly inside the user cookie session
            session['user_role'] = user.role
            session['user_name'] = user.display_name
            session['user_email'] = user.email
            return redirect(url_for('admin.index'))
        flash("Access Denied: Invalid University credentials or server trust error.", "danger")
        
    return render_template_string('''
        <div style="max-width:360px; margin:80px auto; font-family:sans-serif; text-align:center; box-shadow:0 0 10px rgba(0,0,0,0.1); padding:20px;">
            <h2 style="color:#1A365D;">Algic Corpus Workspace</h2>
            <p style="font-size:12px; color:#718096;">Identify using an authorized access provider</p>
            <form method="post" style="margin-bottom:20px; text-align:left;">
                <input type="text" name="username" placeholder="University ShortID / UID" required style="width:95%; margin-bottom:10px; padding:10px;"><br>
                <input type="password" name="password" placeholder="Password" required style="width:95%; margin-bottom:10px; padding:10px;"><br>
                <button type="submit" style="width:100%; padding:10px; background:#1A365D; color:white; border:none; cursor:pointer;">Sign In via Active Directory</button>
            </form>
            <div style="margin:15px 0; color:#CBD5E0;">─── OR ───</div>
            <a href="{{ url_for('auth_portal.sso_login') }}" style="display:block; margin-bottom:8px; padding:10px; background:#4A5568; color:white; text-decoration:none; font-size:14px;">Institutional SAML Gateway</a>
            <a href="{{ url_for('auth_portal.google_login') }}" style="display:block; padding:10px; background:#EA4335; color:white; text-decoration:none; font-size:14px;">Sign in with Google Account</a>
        </div>
    ''')

# --- SHUNT SAML PROTOCOLS ---
@auth_bp.route('/sso/login/', endpoint='sso_login')
def sso_login():
    return saml_adapter.saml_login()

@auth_bp.route('/sso/metadata/', endpoint='sso_metadata')
def sso_metadata():
    return saml_adapter.metadata()

@auth_bp.route('/sso/authorize/', endpoint='sso_authorize', methods=['POST'])
def sso_authorize():
    response = saml_adapter.authorize()
    if response:
        attributes = session.get('SSO_ATTRIBUTES', {})
        # Assign admin access privileges if university staff attributes match
        role = "admin" if "staff" in attributes.get('eduPersonAffiliation', []) else "researcher"
        
        user = AuthenticatedLinguist(
            user_id=session.get('SSO_NAMEID', 'saml_user'),
            display_name=attributes.get('cn', ['SAML User'])[0],
            email=attributes.get('mail', [''])[0],
            role=role,
            provider="saml"
        )
        login_user(user)
        session['user_role'] = user.role
    return redirect(url_for('admin.index'))

# --- SHUNT GOOGLE OPENID OAUTH ---
@auth_bp.route('/auth/google')
def google_login():
    redirect_uri = url_for('auth_portal.google_authorize', _external=True)
    return oauth_client.google.authorize_redirect(redirect_uri)

@auth_bp.route('/auth/google/callback')
def google_authorize():
    token = oauth_client.google.authorize_access_token()
    user_info = token.get('userinfo')
    if user_info:
        # Social users default to the "researcher" role unless manually overridden
        user = AuthenticatedLinguist(
            user_id=user_info['sub'],
            display_name=user_info['name'],
            email=user_info['email'],
            role="researcher",
            provider="google"
        )
        login_user(user)
        session['user_role'] = user.role
        session['user_name'] = user.display_name
        session['user_email'] = user.email
        return redirect(url_for('admin.index'))
    return redirect(url_for('auth_portal.universal_login'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth_portal.universal_login'))

# -------------------------------------------------------------------
# E. APPLICATION FACTORY LINKAGE INTERFACE
# -------------------------------------------------------------------
def init_auth(app):
    """Registers authentication managers and drivers with the core Flask context."""
    login_manager = LoginManager(app)
    login_manager.login_view = "auth_portal.universal_login"
    
    @login_manager.user_loader
    def user_loader(user_id):
        if 'SSO_NAMEID' in session:
            return saml_adapter.user(user_id)
        # Re-hydrate the current user's session from secure cookies
# Admin/login.py (Excerpt update inside your universal_login view function)
from flask import request, g
from Admin.bg_admin import BackgroundAdminMonitor

# Inside your Blueprint registration or view file context...
@auth_bp.route('/login', methods=['GET', 'POST'])
def universal_login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        
        if username == SecurityRecoveryConfig.EMERGENCY_ADMIN_USER:
            if check_password_hash(SecurityRecoveryConfig.EMERGENCY_HASHED_KEY, password):
                # Trigger the background monitor
                bg_monitor = BackgroundAdminMonitor(auth_bp.get_app() if hasattr(auth_bp, 'get_app') else None)
                operator_ip = request.remote_addr or "127.0.0.1"
                
                # Run the notification pipeline in the background
                bg_monitor.trigger_break_glass_alert(operator_ip=operator_ip)
                
                # Log the user into their session context
                emergency_user = AuthenticatedLinguist(username, "System Break-Glass Operator", "admin@uni.edu", role="admin")
                login_user(emergency_user)
                return redirect(url_for('admin.index'))
